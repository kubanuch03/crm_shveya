# app_productions/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction, models
from django.utils import timezone
from django.db.models import Sum
from .models import ProcessStage, WorkLog, Product
from app_accounting.models import UserSalary
from app_accounting.services.user_salary import Payment
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

# --- Константы для логики ---
FINAL_STATUS_FOR_UPDATE = 'CONFIRMED'
PACKING_STAGE_TYPE = 'PACKING'


@receiver(post_save, sender=WorkLog)
def handle_work_log_save(sender, instance: WorkLog, created: bool, **kwargs):
    """
    ЕДИНЫЙ обработчик для сохранения WorkLog.
    Пересчитывает зарплату (UserSalary) для пользователя.
    """
    payment_calculator = Payment()
    work_log_user = instance.user

    if not instance.log_time:
        logger.error(f"WorkLog {instance.pk} не имеет log_time. Невозможно определить период зарплаты.")
        return

    target_year = instance.log_time.year
    target_month = instance.log_time.month
    
    try:
        with transaction.atomic():
            user_salary, created_now = UserSalary.objects.select_for_update().get_or_create(
                user=work_log_user,
                salary_year=target_year,
                salary_month=target_month,
                is_paid=False,
                defaults={'total_cash': Decimal('0.00')}
            )
            user_salary.work_log.add(instance)

            new_total_cash = Decimal('0.00')
            
            # === ПРАВИЛЬНЫЙ ЗАПРОС ДЛЯ ВАШЕЙ СТРУКТУРЫ ===
            all_related_work_logs = user_salary.work_log.all().select_related(
                'stage',
                'stage__batch_product',
                'stage__batch_product__batch'
            ).prefetch_related(
                'stage__batch_product__product' # prefetch для ManyToMany
            )

            for log_entry in all_related_work_logs:
                if not log_entry.stage or not log_entry.stage.batch_product:
                    logger.warning(f"Пропуск WorkLog {log_entry.pk}: нет связи stage или batch_product.")
                    continue

                products_to_process = log_entry.stage.batch_product.product.all()
                
                if not products_to_process:
                    logger.warning(f"Пропуск WorkLog {log_entry.pk}: у BatchProduct {log_entry.stage.batch_product.pk} нет товаров.")
                    continue
                
                for product_instance in products_to_process:
                    action_type = log_entry.stage.stage_type
                    rate_for_action = payment_calculator.get_rate_for_action(action_type, product_instance)

                    if rate_for_action and rate_for_action > Decimal('0.00') and log_entry.quantity_processed > 0:
                        earnings_for_log = Decimal(log_entry.quantity_processed) * rate_for_action
                        new_total_cash += earnings_for_log
                        # Если ставка должна считаться один раз на всю партию, а не на каждый товар,
                        # добавьте здесь `break`. Сейчас считается для каждого товара.

            if user_salary.total_cash != new_total_cash:
                user_salary.total_cash = new_total_cash
                user_salary.save(update_fields=['total_cash'])
                logger.info(f"UserSalary для {work_log_user.username} за {target_month:02d}/{target_year} обновлена. Новый total_cash: {new_total_cash:.2f}")

    except Exception as e:
        logger.error(f"Критическая ошибка в сигнале handle_work_log_save (WorkLog ID: {instance.pk}): {e}", exc_info=True)


@receiver(post_save, sender=ProcessStage)
def handle_process_stage_save(sender, instance: ProcessStage, created: bool, **kwargs):
    """
    ЕДИНЫЙ обработчик для сохранения ProcessStage.
    """
    # 1. Создание/обновление WorkLog
    if instance.status == FINAL_STATUS_FOR_UPDATE and instance.assigned_user and instance.quantity_completed > 0:
        log_timestamp = instance.end_date or instance.updated_at or timezone.now()
        WorkLog.objects.update_or_create(
            stage=instance, user=instance.assigned_user,
            defaults={
                'quantity_processed': instance.quantity_completed,
                'quantity_defective': instance.quantity_deffect or 0,
                'log_time': log_timestamp
            }
        )

    # 2. Обновление quantity_finish у BatchProduct
    if instance.stage_type == PACKING_STAGE_TYPE and instance.batch_product:
        total_packed = ProcessStage.objects.filter(
            batch_product=instance.batch_product,
            stage_type=PACKING_STAGE_TYPE,
            status=FINAL_STATUS_FOR_UPDATE
        ).aggregate(total=Sum('quantity_completed'))['total'] or 0

        if instance.batch_product.quantity_finish != total_packed:
            instance.batch_product.quantity_finish = total_packed
            instance.batch_product.save(update_fields=['quantity_finish'])

    # 3. Закрытие партии (ProductionBatch)
    if instance.status == FINAL_STATUS_FOR_UPDATE and instance.batch_product:
        batch = instance.batch_product.batch
        all_stages_count = ProcessStage.objects.filter(batch_product__batch=batch).count()
        completed_stages_count = ProcessStage.objects.filter(
            batch_product__batch=batch, 
            status=FINAL_STATUS_FOR_UPDATE
        ).count()

        if all_stages_count > 0 and all_stages_count == completed_stages_count:
            if not batch.is_completed:
                batch.is_completed = True
                batch.save(update_fields=['is_completed'])
                logger.info(f"Партия {batch.id} ({batch.batch_number}) была закрыта.")