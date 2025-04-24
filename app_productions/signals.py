# productions/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import ProcessStage, BatchProduct, ProductionBatch, Product
from logger import logger


FINAL_STATUS_FOR_UPDATE = 'CONFIRMED'
LAST_STAGE_TYPE = 'PACKING'







@receiver(post_delete, sender=ProcessStage)
def remains_plus_product(sender, instance, using, **kwargs):
    obj = instance.batch_product.product.title
    product = Product.objects.filter(title=obj).first()
    complated = instance.quantity_completed
    deffective = instance.quantity_defective
    product_remains = product.remains

    if complated and deffective:
        product.remains= product_remains+(complated+deffective)
        product.save()
    return False



# @receiver(post_save, sender=ProcessStage)
# def remains_minus_product(sender, instance, created, **kwargs):
#     if instance.quantity_completed and instance.quantity_defective:
#             total_completed = instance.quantity_completed + instance.quantity_defective 
#             logger.debug(f'total delta: {total_completed}')
#             product_title = instance.batch_product.product.title
#             logger.debug(f'product: {product_title}')
#     logger.debug(f'remains_minus_product')
#     if instance.stage_type=="Упаковка":
#             logger.info("stage type упаковка")
#             product = Product.objects.filter(title=product_title).first()
#             product.remains -= total_completed
#             product.save()

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