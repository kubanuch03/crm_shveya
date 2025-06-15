# app_productions/models.py
from django.db import models, transaction
from django.db.models import F, Sum
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
# УДАЛИТЬ, если не используешь JSONField в Product: from django.db.models import JSONField 
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.contrib import admin

from app_users.models import User
# Убедись, что Payment импортирован из правильного места, если он нужен здесь (он нужен для get_total_earnings_for_batch)
from app_accounting.services.user_salary import Payment 

import logging
logger = logging.getLogger(__name__)

OPERATION_TYPE_CHOICES = (
    ('SEWING', _('Шитье')),
    ('UTUG', _('Утюг')),
    ('PACKING', _('Упаковка')),
    ('CUTTING', _('Крой')),
    ('BUTTONS', _('Пуговица')),
    ('QC', _('Контроль качества')),
)

class Color(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Название'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создание'))
    def __str__(self): return f"{self.title}" if self.title else f"Color {self.id}"
    class Meta: verbose_name = _("Цвет Товара"); verbose_name_plural = _("Цвет Товара"); ordering = ['title']

class Size(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Название'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создание'))
    def __str__(self): return f"{self.title}" if self.title else f"Size {self.id}"
    class Meta: verbose_name = _("Размер Товара"); verbose_name_plural = _("Размер Товара"); ordering = ['title']

class Category(models.Model):
    title = models.CharField(max_length=255, verbose_name=_('Название'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создание'))
    def __str__(self): return f"{self.title}" if self.title else f"Category {self.id}"
    class Meta: verbose_name = _("Категория Товара"); verbose_name_plural = _("Категория Товара"); ordering = ['title']

class Product_Model(models.Model): # Рекомендую ProductModel
    title = models.CharField(max_length=255, verbose_name=_('Название'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создание'))
    def __str__(self): return f"{self.title}" if self.title else f"Model {self.id}"
    class Meta: verbose_name = _("Модель Товара"); verbose_name_plural = _("Модели Товара"); ordering = ['title']

class Product(models.Model):
    title = models.CharField(max_length=255, blank=False, null=False, verbose_name=_('Название'))
    color = models.ManyToManyField('Color', blank=True, verbose_name=_('Цвет'))
    size = models.ManyToManyField('Size', blank=True, verbose_name=_('Размер '))
    category = models.ManyToManyField('Category', blank=True, verbose_name=_('Категория'))
    product_model = models.ManyToManyField('Product_Model', blank=True, verbose_name=_('Модель'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создание'))
 

    def __str__(self):
        return f"{self.title}" if self.title else f"Product {self.id}"

    def get_individual_rate_for_operation(self, operation_type: str) -> Decimal | None:
        # Этот метод для варианта с ProductOperationRate (Решение 1)
        try:
            # Убедись, что 'operation_rates' - это related_name в ProductOperationRate.product
            rate_obj = self.operation_rates.get(operation_type=operation_type)
            return rate_obj.rate
        except ProductOperationRate.DoesNotExist:
            return None
        except Exception as e:
            logger.error(f"Ошибка при получении индивидуальной ставки для {self.title} ({operation_type}): {e}")
            return None
        
        

    class Meta:
        verbose_name = _("Товар")
        verbose_name_plural = _("Товары")
        ordering = ['title']

# Модель для Решения 1 (индивидуальные ставки через связанную модель)
class ProductOperationRate(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='operation_rates', 
        verbose_name=_("Товар")
    )
    operation_type = models.CharField(
        max_length=20,
        choices=OPERATION_TYPE_CHOICES, 
        verbose_name=_('Тип операции')
    )
    rate = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name=_('Индивидуальная ставка')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.title} - {self.get_operation_type_display()}: {self.rate}"

    class Meta:
        verbose_name = _("Индивидуальная ставка для товара")
        verbose_name_plural = _("Индивидуальные ставки для товаров")
        unique_together = ('product', 'operation_type')
        ordering = ['product', 'operation_type']


class ProductionBatch(models.Model):
    batch_number = models.CharField(max_length=100, unique=True, blank=True, null=True, verbose_name=_('Номер партии'))
    title = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('Наименование'))
    planned_completion_date = models.DateField(null=True, blank=True, verbose_name=_('Плановая дата завершения'))
    notes = models.TextField(blank=True, null=True, verbose_name=_('Примечания'))
    is_completed = models.BooleanField(default=False, verbose_name=_('Партия завершена'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))

    def get_total_earnings_for_batch(self) -> Decimal:
        total_earnings = Decimal('0.00')
        payment_calculator = Payment() 
        work_logs_for_batch = WorkLog.objects.filter(
            stage__batch_product__batch=self
        ).select_related(
            'stage__batch_product__product'
        )
        for log in work_logs_for_batch:
            if not log.stage or not log.stage.batch_product or not log.stage.batch_product.product:
                logger.warning(f"WorkLog {log.pk} для партии {self.pk} не имеет полного пути к товару. Пропускается.")
                continue
            product_instance = log.stage.batch_product.product
            action_type = log.stage.stage_type
            rate_val = payment_calculator.get_rate_for_action(action_type, product_instance)
            try:
                rate = Decimal(str(rate_val))
            except: rate = Decimal('0.00')
            if rate > Decimal('0.00') and log.quantity_processed > 0:
                total_earnings += Decimal(log.quantity_processed) * rate
        return total_earnings

    @admin.display(description=_("Общий заработок за партию (сом)"))
    def display_total_batch_earnings(self):
        try:
            return f"{self.get_total_earnings_for_batch():.2f}"
        except Exception as e:
            logger.error(f"Ошибка расчета заработка для партии {self.pk}: {e}", exc_info=True)
            return _("Ошибка расчета")

    def __str__(self):
        return f"№:{self.batch_number} {self.title or ''}".strip()
    class Meta:
        verbose_name = _("Производственная партия"); verbose_name_plural = _("Производственные партии"); ordering = ['-created_at']



class BatchProduct(models.Model):
    batch = models.ForeignKey(ProductionBatch, related_name='products_in_batch', on_delete=models.CASCADE, verbose_name=_('Партия'))
    product = models.ManyToManyField(Product, verbose_name=_('Товар'))
    quantity_finish = models.PositiveIntegerField(default=0, verbose_name=_('Количество Готово (итоговое)'))
    def __str__(self): return f"(Партия: {(self.batch.batch_number if self.batch else 'N/A')})"
    class Meta: 
        unique_together = ('batch',) 
        verbose_name = _("Товар в партии")
        verbose_name_plural = _("Товары в партии")
        ordering = ['batch',]


class ProcessStage(models.Model):
    # ... (без изменений, но проверь STAGE_CHOICES и OPERATION_TYPE_CHOICES) ...
    # Убедись, что STAGE_CHOICES здесь и OPERATION_TYPE_CHOICES наверху файла совпадают или коррелируют
    STAGE_CHOICES = OPERATION_TYPE_CHOICES 
    STATUS_CHOICES = (('READY', _('Готово к работе')),('COMPLETED', _('Завершено')), ('CONFIRMED', _('Подтверждено')), ('PLANNED', _('Запланировано'))) # Добавил PLANNED

    batch_product = models.ForeignKey(BatchProduct, on_delete=models.CASCADE, related_name='stages', verbose_name=_('Товар в партии'))
    stage_type = models.CharField(max_length=20, choices=STAGE_CHOICES, verbose_name=_('Тип этапа'))
    assigned_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name=_('Ответственный/Исполнитель'), related_name='assigned_process_stages')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PLANNED', verbose_name=_('Статус'))
    quantity_completed = models.PositiveIntegerField(default=0, verbose_name=_('Выполнено Итого (выход)'))
    quantity_deffect = models.PositiveIntegerField(default=0, verbose_name=_('Брак Итого (на этом этапе)'))
    # ... остальные поля ...
    start_date = models.DateTimeField(null=True, blank=True, verbose_name=_('Дата Начала'))
    end_date = models.DateTimeField(null=True, blank=True, verbose_name=_('Дата Окончания'))
    confirmed_by = models.ForeignKey(User, related_name='confirmed_stages', null=True, blank=True, on_delete=models.SET_NULL, verbose_name=_('Подтвердил'))
    confirmed_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Дата подтверждения'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания записи этапа'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Обновлено'))
    close_session = models.BooleanField(default=False, verbose_name=_('Сессия закрыта (Работа завершена)'))

    def __str__(self): return f"{self.get_stage_type_display()} - {str(self.batch_product) if self.batch_product else 'N/A'} ({self.get_status_display()})"
    class Meta: verbose_name = _("Этап процесса"); verbose_name_plural = _("Этапы процессов"); ordering = ['batch_product__batch__batch_number', 'batch_product__product__title', 'created_at']


class WorkLog(models.Model):
    stage = models.ForeignKey(ProcessStage, on_delete=models.CASCADE, related_name='work_logs', verbose_name=_('Этап процесса'))
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='work_logs', verbose_name=_('Сотрудник'))
    quantity_processed = models.PositiveIntegerField(default=0, verbose_name=_('Обработано штук (за эту запись)'))
    quantity_defective = models.PositiveIntegerField(default=0, verbose_name=_('Обнаружено брака (за эту запись)'))
    log_time = models.DateTimeField(default=timezone.now, verbose_name=_('Время записи лога'))
    notes = models.TextField(blank=True, null=True, verbose_name=_('Примечания'))
    created_at = models.DateTimeField(auto_now_add=True, null=True, verbose_name='Дата Создание')
    def __str__(self): return f"{(self.user.get_full_name() or self.user.username)} - {self.stage} - Qty: {self.quantity_processed} (Def: {self.quantity_defective}) @ {self.log_time.strftime('%Y-%m-%d %H:%M')}"
    def clean(self):
        if self.quantity_defective > self.quantity_processed: raise ValidationError(_('Количество брака не может превышать количество обработанных.'))
    class Meta: verbose_name = _("Запись о выполненной работе"); verbose_name_plural = _("Записи о выполненной работе")