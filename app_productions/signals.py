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


FINAL_STATUS_FOR_UPDATE = 'CONFIRMED'
LAST_STAGE_TYPE = 'PACKING'

@receiver(post_save, sender=WorkLog)
def update_or_create_user_salary_on_worklog_save(sender, instance: WorkLog, created: bool, **kwargs):
    payment_calculator = Payment()
    work_log_user = instance.user
    if not instance.log_time:
        print(f"Ошибка: WorkLog {instance.pk} не имеет log_time. Невозможно определить период зарплаты.")
        return

    target_year = instance.log_time.year
    target_month = instance.log_time.month

    salary_period_for_month = date(target_year, target_month, 1)

    try:
        user_salary, salary_was_created_now = UserSalary.objects.get_or_create(
        user=work_log_user,
        salary_year=target_year,
        salary_month=target_month,
        defaults={
            'salary_period_date': salary_period_for_month,
            }
        )
        user_salary.work_log.add(instance)  

        action = instance.stage.stage_type
        rate_for_action = payment_calculator.get_rate_for_action(action) 

        if rate_for_action > 0:  
            aggregation_result = user_salary.work_log.aggregate(
                total_quantity=Coalesce(Sum('quantity_processed'), Value(0), output_field=IntegerField())
            )
            new_total_cash = aggregation_result['total_quantity'] * rate_for_action
        else:
            new_total_cash = 0  

        if user_salary.total_cash != new_total_cash or salary_was_created_now:
            user_salary.total_cash = new_total_cash
            user_salary.save(update_fields=['total_cash', 'salary_period_date']) 
            status_msg = "создана и рассчитана" if salary_was_created_now else "обновлена и пересчитана"
            logger.info(f"UserSalary для {work_log_user.username} за {target_month}/{target_year} {status_msg}. Новый total_cash: {new_total_cash}")
        else:
            logger.info(f"UserSalary для {work_log_user.username} за {target_month}/{target_year} не требовала обновления total_cash.")
    except Exception as e:
        logger.error(f"User: {work_log_user} {e} ")
        raise


@receiver(post_save, sender=ProcessStage)
def create_work_log_on_process_stage_save(sender, instance: ProcessStage, created: bool, **kwargs):
    logger.info(f"create_work_log_on_process_stage_save")
    log_timestamp = instance.completed_at if hasattr(instance, 'completed_at') and instance.completed_at else timezone.now()

    if instance.assigned_user and instance.quantity_completed is not None:
        if instance.status == "CONFIRMED":
            log_timestamp = instance.completed_at if hasattr(instance, 'completed_at') and instance.completed_at else timezone.now()

            
            work_log_object, wl_created = WorkLog.objects.update_or_create(
                stage=instance,        
                user=instance.assigned_user,  
                defaults={
                    'quantity_processed': instance.quantity_completed,
                    'quantity_defective': instance.quantity_deffect if hasattr(instance, 'quantity_deffect') else 0,
                    'log_time': log_timestamp
                    
                }
            )

            if wl_created:
                logger.info(f"WorkLog СОЗДАН (ID: {work_log_object.id}) для ProcessStage {instance.id}")
            else:
                logger.info(f"WorkLog ОБНОВЛЕН (ID: {work_log_object.id}) для ProcessStage {instance.id}")
        else:
            logger.info(f"WorkLog не создан/обновлен для ProcessStage {instance.id}, так как статус не 'CONFIRMED' (текущий: {instance.status}).")
    else:
        missing_parts = []
        if not instance.assigned_user:
            missing_parts.append("assigned_user")
        if instance.quantity_completed is None:
            missing_parts.append("quantity_completed")
        logger.error(f"WorkLog не создан/обновлен для ProcessStage {instance.id}: отсутствует {', '.join(missing_parts)}.")



def update_batch_product_finish_quantity(batch_product):
    """
    Пересчитывает и сохраняет quantity_finish для заданного BatchProduct
    на основе всех его этапов упаковки.
    """
    if batch_product is None:
        return

    aggregation = ProcessStage.objects.filter(
        batch_product=batch_product,
        stage_type="PACKING"
    ).aggregate(
        total_completed=Coalesce(Sum('quantity_completed'), Value(0), output_field=IntegerField()),
        total_defective=Coalesce(Sum('quantity_deffect'), Value(0), output_field=IntegerField())
    )

    new_finish_quantity = aggregation['total_completed'] + aggregation['total_defective']

    if batch_product.quantity_finish != new_finish_quantity:
        batch_product.quantity_finish = new_finish_quantity
        batch_product.save(update_fields=['quantity_finish'])


@receiver(post_save, sender=ProcessStage)
def process_stage_post_save(sender, instance, created, **kwargs):
    """
    Вызывается после сохранения ProcessStage.
    Если это этап упаковки, пересчитывает итог для связанного BatchProduct.
    """
    if instance.stage_type == "PACKING":
        update_batch_product_finish_quantity(instance.batch_product)




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