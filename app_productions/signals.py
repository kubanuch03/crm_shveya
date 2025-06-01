# productions/signals.py

from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver
from .models import ProcessStage, BatchProduct, ProductionBatch, Product, WorkLog
from logger import logger
from django.db.models.functions import Coalesce
from django.db.models import Sum, Value, IntegerField
from django.utils.timezone import make_aware
from datetime import datetime
from django.db import transaction
from django.utils import timezone
from datetime import date
from app_accounting.models import UserSalary
from app_accounting.services.user_salary import Payment
from app_global.models import PackagingSettings, UtugSettings, TailorSettings


from decimal import Decimal

FINAL_STATUS_FOR_UPDATE = 'CONFIRMED'
LAST_STAGE_TYPE = 'PACKING'
@receiver(post_save, sender=WorkLog)
def update_or_create_user_salary_on_worklog_save(sender, instance: WorkLog, created: bool, **kwargs):
    payment_calculator = Payment()
    work_log_user = instance.user

    if not instance.log_time: # log_time WorkLog'а определяет, к какому месяцу он относится
        logger.error(f"WorkLog {instance.pk} не имеет log_time.")
        return

    target_year = instance.log_time.year
    target_month = instance.log_time.month

    try:
        with transaction.atomic():
            # Ищем самый последний НЕВЫПЛАЧЕННЫЙ UserSalary для этого пользователя и этого месяца
            active_salary_period = UserSalary.objects.filter(
                user=work_log_user,
                salary_year=target_year,
                salary_month=target_month,
                is_paid=False
            ).order_by('-period_start_datetime').first()

            salary_was_created_now = False
            if not active_salary_period:
                # Если нет активного периода за этот месяц, создаем новый
                active_salary_period = UserSalary.objects.create(
                    user=work_log_user,
                    salary_year=target_year,
                    salary_month=target_month,
                    period_start_datetime=timezone.now(), # или instance.log_time, если это первый лог
                    total_cash=Decimal('0.00'),
                    is_paid=False
                )
                salary_was_created_now = True
                logger.info(f"Создан новый UserSalary ID {active_salary_period.pk} для {work_log_user.username} за {target_month:02d}/{target_year}.")
            
            user_salary = active_salary_period # Теперь работаем с ним

            # Добавляем WorkLog к UserSalary M2M
            if created or not user_salary.work_log.filter(pk=instance.pk).exists():
                 user_salary.work_log.add(instance)

            # Пересчитываем total_cash для ТЕКУЩЕГО АКТИВНОГО ПЕРИОДА user_salary
            new_total_cash = Decimal('0.00')
            # Важно: агрегируем WorkLog'и, которые были созданы НЕ РАНЕЕ, чем period_start_datetime текущего user_salary
            # И которые еще не привязаны к другому, уже выплаченному, UserSalary за этот же месяц.
            # Это усложняет выборку WorkLog'ов для подсчета.
            # Простой вариант: просто суммировать все из user_salary.work_log.all()
            # Сложный вариант: убедиться, что work_log.log_time >= user_salary.period_start_datetime
            # И work_log еще не в другом UserSalary, который is_paid=True и имеет более ранний period_start_datetime

            # ---- ПРОСТОЙ ВАРИАНТ (может быть неточным, если WorkLog'и могут перепрыгивать между периодами) ---
            all_related_work_logs = user_salary.work_log.all().select_related(
                'stage__batch_product__product'
            )
            # ---- КОНЕЦ ПРОСТОГО ВАРИАНТА ---
            # Для более точного, нужно фильтровать work_log по датам относительно period_start_datetime


            for log_entry in all_related_work_logs:
                # ... (логика расчета earnings_for_log остается такой же) ...
                if not log_entry.stage or not log_entry.stage.batch_product or not log_entry.stage.batch_product.product:
                    logger.warning(f"Пропуск WorkLog {log_entry.pk} при расчете ЗП: нет полного пути к товару.")
                    continue
                product_instance = log_entry.stage.batch_product.product
                action_type = log_entry.stage.stage_type
                rate_val = payment_calculator.get_rate_for_action(action_type, product_instance)
                try: rate = Decimal(str(rate_val))
                except: rate = Decimal('0.00')
                if rate > Decimal('0.00') and log_entry.quantity_processed > 0:
                    new_total_cash += Decimal(log_entry.quantity_processed) * rate
            
            if user_salary.total_cash != new_total_cash or salary_was_created_now:
                user_salary.total_cash = new_total_cash
                user_salary.save(update_fields=['total_cash'])
                status_msg = "создана и рассчитана" if salary_was_created_now else "обновлена и пересчитана"
                logger.info(f"UserSalary ID {user_salary.pk} для {work_log_user.username} (период с {user_salary.period_start_datetime}) {status_msg}. Новый total_cash: {new_total_cash:.2f}")
            # ... (остальной лог)
    except Exception as e:
        logger.error(f"Критическая ошибка в сигнале update_or_create_user_salary (WorkLog: {instance.pk}): {e}", exc_info=True)

@receiver(post_save, sender=ProcessStage)
def create_work_log_on_process_stage_save(sender, instance: ProcessStage, created: bool, **kwargs):
    logger.info(f"create_work_log_on_process_stage_save") # Это строка 103 в твоем логе
    # ...
    # У тебя был лог instance.completed_at, я его убрал, так как он может быть None
    # log_timestamp = instance.completed_at if hasattr(instance, 'completed_at') and instance.completed_at else timezone.now() 
    # Лучше так:
    log_timestamp = timezone.now() # По умолчанию текущее время
    if hasattr(instance, 'end_date') and instance.end_date: # Если есть end_date у этапа
        log_timestamp = instance.end_date
    elif hasattr(instance, 'completed_at') and instance.completed_at: # Или completed_at (если такое поле есть)
         log_timestamp = instance.completed_at
    elif instance.status in ['COMPLETED', 'CONFIRMED'] and instance.updated_at: # Если завершен и есть updated_at
        log_timestamp = instance.updated_at


    if instance.assigned_user and instance.quantity_completed is not None and instance.quantity_completed > 0: # Добавил > 0
        # Создаем WorkLog, только если статус подходящий
        if instance.status == "CONFIRMED": # Или 'COMPLETED', или оба ['COMPLETED', 'CONFIRMED']
            
            # Важно: Используй transaction.atomic, если хочешь, чтобы создание WorkLog и 
            # последующий вызов сигнала для UserSalary были в одной транзакции.
            # Но здесь мы просто создаем WorkLog.
            try:
                work_log_object, wl_created = WorkLog.objects.update_or_create(
                    stage=instance,        
                    user=instance.assigned_user,  
                    # Если ты хочешь ОДИН WorkLog на связку stage-user, то это правильно.
                    # Если может быть МНОГО WorkLog'ов от одного юзера на один stage (например, он несколько раз докладывал о работе),
                    # то update_or_create не подходит, нужно просто WorkLog.objects.create(...)
                    defaults={
                        'quantity_processed': instance.quantity_completed,
                        'quantity_defective': instance.quantity_deffect if hasattr(instance, 'quantity_deffect') else 0,
                        'log_time': log_timestamp 
                        # 'notes': "Автоматически создано из ProcessStage" # Можно добавить примечание
                    }
                )

                if wl_created:
                    logger.info(f"WorkLog СОЗДАН (ID: {work_log_object.id}) для ProcessStage {instance.id}") # Это строка 123
                else:
                    logger.info(f"WorkLog ОБНОВЛЕН (ID: {work_log_object.id}) для ProcessStage {instance.id}")
            except Exception as e:
                logger.error(f"Ошибка при создании/обновлении WorkLog для ProcessStage {instance.id}: {e}", exc_info=True)

        else:
            logger.info(f"WorkLog не создан/обновлен для ProcessStage {instance.id}, так как статус не 'CONFIRMED' (текущий: {instance.status}).")
    else:
        missing_parts = []
        if not instance.assigned_user:
            missing_parts.append("assigned_user не назначен")
        if instance.quantity_completed is None:
            missing_parts.append("quantity_completed не указано")
        elif instance.quantity_completed <= 0 : # Добавил проверку
             missing_parts.append("quantity_completed равно 0 или меньше")
        
        if missing_parts:
             logger.warning(f"WorkLog не создан/обновлен для ProcessStage {instance.id}: {', '.join(missing_parts)}.")


@receiver(post_save, sender=WorkLog)
def update_or_create_user_salary_on_worklog_save(sender, instance: WorkLog, created: bool, **kwargs):
    payment_calculator = Payment()
    work_log_user = instance.user

    if not instance.log_time:
        logger.error(f"WorkLog {instance.pk} не имеет log_time. Невозможно определить период зарплаты.")
        return

    target_year = instance.log_time.year
    target_month = instance.log_time.month
    
    try:
        with transaction.atomic():
            user_salary, salary_was_created_now = UserSalary.objects.select_for_update().get_or_create(
                user=work_log_user,
                salary_year=target_year,
                salary_month=target_month,
                defaults={
                    'salary_period_date': date(target_year, target_month, 1),
                    'total_cash': Decimal('0.00'),
                    'is_paid': False, 
                    'paid_at': None,
                    'paid_by': None
                }
            )

            # Добавляем WorkLog к UserSalary M2M
            if created or not user_salary.work_log.filter(pk=instance.pk).exists():
                 user_salary.work_log.add(instance)

            # Пересчитываем total_cash
            new_total_cash = Decimal('0.00')
            all_related_work_logs = user_salary.work_log.all().select_related(
                'stage__batch_product__product' # Основной путь к товару
            )

            for log_entry in all_related_work_logs:
                if not log_entry.stage or \
                   not log_entry.stage.batch_product or \
                   not log_entry.stage.batch_product.product:
                    logger.warning(f"WorkLog {log_entry.pk} (UserSalary {user_salary.pk}) не имеет полного пути к товару. Пропускается при расчете ЗП.")
                    continue
                
                product_instance = log_entry.stage.batch_product.product
                action_type = log_entry.stage.stage_type
                
                rate_for_action = payment_calculator.get_rate_for_action(action_type, product_instance)
                # get_rate_for_action уже должен возвращать Decimal

                if rate_for_action > Decimal('0.00') and log_entry.quantity_processed > 0:
                    earnings_for_log = Decimal(log_entry.quantity_processed) * rate_for_action
                    new_total_cash += earnings_for_log
            
            if user_salary.total_cash != new_total_cash or salary_was_created_now:
                user_salary.total_cash = new_total_cash
                
                # Логика переоткрытия периода, если работа добавлена в уже закрытый
                # Это опционально и зависит от бизнес-требований
                update_fields_list = ['total_cash']
                if user_salary.is_paid and not salary_was_created_now: # Если нашли существующий закрытый период
                    logger.warning(f"Работа WorkLog ID {instance.pk} добавляется к УЖЕ ЗАКРЫТОМУ UserSalary ID {user_salary.pk}. Сумма будет пересчитана.")
                    # Если нужно переоткрыть:
                    # user_salary.is_paid = False
                    # user_salary.paid_at = None
                    # user_salary.paid_by = None
                    # update_fields_list.extend(['is_paid', 'paid_at', 'paid_by'])
                    # logger.info(f"UserSalary {user_salary.pk} был(а) переоткрыт(а) из-за добавления нового WorkLog.")

                user_salary.save(update_fields=update_fields_list)
                status_msg = "создана и рассчитана" if salary_was_created_now else "обновлена и пересчитана"
                logger.info(f"UserSalary для {work_log_user.username} за {target_month:02d}/{target_year} {status_msg}. Новый total_cash: {new_total_cash:.2f}")
            else:
                logger.info(f"UserSalary для {work_log_user.username} за {target_month:02d}/{target_year} не требовала обновления total_cash (текущий: {user_salary.total_cash:.2f}).")

    except Exception as e:
        logger.error(f"Критическая ошибка в сигнале update_or_create_user_salary (WorkLog ID: {instance.pk}, User: {work_log_user.username}): {e}", exc_info=True)


# --- Функция, которую вы, вероятно, хотели вызвать ---
def update_batch_product_finish_quantity(batch_product): # Эта функция у вас уже есть
    """
    Пересчитывает и сохраняет quantity_finish для заданного BatchProduct
    на основе всех его этапов упаковки.
    """
    if batch_product is None:
        logger.warning("update_batch_product_finish_quantity вызван с batch_product=None")
        return

    # Убедитесь, что ProcessStage импортирован и доступен
    aggregation = ProcessStage.objects.filter(
        batch_product=batch_product,
        stage_type="PACKING" # Предполагаем, что PACKING - это финальный этап для quantity_finish
    ).aggregate(
        # Используем Coalesce для обработки случая, когда нет записей
        total_completed=Coalesce(Sum('quantity_completed'), Value(0), output_field=IntegerField()),
        # total_defective=Coalesce(Sum('quantity_deffect'), Value(0), output_field=IntegerField()) # Если брак тоже учитывается в quantity_finish
    )

    # Логика для new_finish_quantity должна соответствовать семантике поля
    # Если quantity_finish - это только годные, то:
    new_finish_quantity = aggregation['total_completed']
    # Если quantity_finish - это общее количество (годные + брак на этапе упаковки), то:
    # new_finish_quantity = aggregation['total_completed'] + aggregation.get('total_defective', 0) # Используем get для безопасности

    if batch_product.quantity_finish != new_finish_quantity:
        batch_product.quantity_finish = new_finish_quantity
        batch_product.save(update_fields=['quantity_finish'])
        logger.info(f"BatchProduct {batch_product.id} quantity_finish обновлен на {new_finish_quantity}")
    else:
        logger.info(f"BatchProduct {batch_product.id} quantity_finish не требует обновления (текущий: {new_finish_quantity})")


@receiver(post_save, sender=ProcessStage)
def process_stage_post_save(sender, instance, created, **kwargs): # <--- Это стандартный обработчик сигнала post_save
    """
    Вызывается после сохранения ProcessStage.
    Если это этап упаковки, пересчитывает итог для связанного BatchProduct.
    """
    if instance.stage_type == "PACKING":
        update_batch_product_finish_quantity(instance.batch_product) #




@receiver(post_save, sender=ProcessStage)
def closed_batch(sender, instance: ProcessStage, created, **kwargs):
    if instance.status in ['CONFIRMED', 'COMPLETED']:
        logger.debug('product confirmed')
        batch = instance.batch_product.batch
        batch.is_completed = True
        batch.save()


@receiver(post_save, sender=ProcessStage)
def update_batch_product_finished_quantity(sender, instance: ProcessStage, created, **kwargs):
    """
    Обновляет поле quantity_finished у BatchProduct, когда последний
    этап (ProcessStage) для этого продукта получает финальный статус.
    """
    is_final_status = instance.status == FINAL_STATUS_FOR_UPDATE

    is_last_stage_by_type = instance.stage_type == LAST_STAGE_TYPE

    is_last_stage_by_link = False
    if hasattr(instance, 'next_stage'):
        try:
            _ = instance.next_stage
        except ProcessStage.DoesNotExist:
             is_last_stage_by_link = True
        except AttributeError: 
            if instance.next_stage is None:
                 is_last_stage_by_link = True


    is_last_stage = is_last_stage_by_link

    if is_final_status and is_last_stage:
        batch_product_to_update = instance.batch_product
        new_finished_quantity = instance.quantity_completed

        BatchProduct.objects.filter(pk=batch_product_to_update.pk).update(
            quantity_finished=new_finished_quantity
        )
        logger.debug(f"Updated BatchProduct {batch_product_to_update.pk} quantity_finished to {new_finished_quantity}") # Лог для отладки

    elif not is_final_status and is_last_stage:
         batch_product_to_update = instance.batch_product
         if batch_product_to_update.quantity_finished != 0:
              BatchProduct.objects.filter(pk=batch_product_to_update.pk).update(
                  quantity_finished=0
              )
              logger.debug(f"Reset BatchProduct {batch_product_to_update.pk} quantity_finished to 0") # Лог для отладки