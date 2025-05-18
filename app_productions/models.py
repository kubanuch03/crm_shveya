from django.db import models, transaction
from django.db.models import F, Sum
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
from django.core.exceptions import ValidationError

from app_users.models import User # Assuming User model is in app_users app

# Assuming logger is configured elsewhere (e.g., in settings.py)
import logging
logger = logging.getLogger(__name__) # Standard Python logging

# --- Basic Attribute Models ---

class Color(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Название'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создание'))

    def __str__(self):
        return f"{self.title}" if self.title else f"Color {self.id}"

    class Meta:
        verbose_name = _("Цвет Товара")
        verbose_name_plural = _("Цвет Товара")
        ordering = ['title']

class Size(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Название'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создание'))

    def __str__(self):
        return f"{self.title}" if self.title else f"Size {self.id}"

    class Meta:
        verbose_name = _("Размер Товара")
        verbose_name_plural = _("Размер Товара")
        ordering = ['title']

class Category(models.Model):
    title = models.CharField(max_length=255, verbose_name=_('Название'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создание'))

    def __str__(self):
        return f"{self.title}" if self.title else f"Category {self.id}"

    class Meta:
        verbose_name = _("Категория Товара")
        verbose_name_plural = _("Категория Товара")
        ordering = ['title']

class Product_Model(models.Model):
    title = models.CharField(max_length=255, verbose_name=_('Название'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создание'))

    def __str__(self):
        return f"{self.title}" if self.title else f"Model {self.id}"

    class Meta:
        verbose_name = _("Модель Товара")
        verbose_name_plural = _("Модели Товара")
        ordering = ['title']

class Product(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Название'))
    color = models.ManyToManyField(Color, blank=True, verbose_name=_('Цвет'))
    size = models.ManyToManyField(Size, blank=True, verbose_name=_('Размер '))
    category = models.ManyToManyField(Category, blank=True, verbose_name=_('Категория'))
    product_model = models.ManyToManyField(Product_Model, blank=True, verbose_name=_('Модель'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создание'))

    def __str__(self):
        return f"{self.title}" if self.title else f"Product {self.id}"

    class Meta:
        verbose_name = _("Товар")
        verbose_name_plural = _("Товары")
        ordering = ['title']

# --- Production Workflow Models ---

class ProductionBatch(models.Model):
    batch_number = models.CharField(max_length=100, unique=True, blank=True, null=True, verbose_name=_('Номер партии'))
    title = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('Наименование'))
    planned_completion_date = models.DateField(null=True, blank=True, verbose_name=_('Плановая дата завершения'))
    notes = models.TextField(blank=True, null=True, verbose_name=_('Примечания'))
    is_completed = models.BooleanField(default=False, verbose_name=_('Партия завершена'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))
    # Optional: Add Filial FK here if needed later
    # filial = models.ForeignKey('your_filial_app.Filial', ...)

    def __str__(self):
        return f"№:{self.batch_number} {self.title or ''}".strip()

    class Meta:
        verbose_name = _("Производственная партия")
        verbose_name_plural = _("Производственные партии")
        ordering = ['-created_at']

class BatchProduct(models.Model):
    batch = models.ForeignKey(ProductionBatch, related_name='products_in_batch', on_delete=models.CASCADE, verbose_name=_('Партия'))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_('Товар'))
    quantity_finish = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Количество Готово (итоговое)'),
        help_text=_('Итоговое количество после завершения всех этапов всей партии')
    )

    def __str__(self):
        product_title = self.product.title if self.product else _("N/A Product")
        batch_number = self.batch.batch_number if self.batch else _("N/A Batch")
        return f"{product_title} ({_('Партия')}: {batch_number})"

    class Meta:
        unique_together = ('batch', 'product')
        verbose_name = _("Товар в партии")
        verbose_name_plural = _("Товары в партии")
        ordering = ['batch', 'product']

class ProcessStage(models.Model):
    STAGE_CHOICES = (
        ('SEWING', _('Шитье')),
        ('UTUG', _('Утюг')), # 
        ('PACKING', _('Упаковка')),
        ('CUTTING', _('Крой')),
        ('BUTTONS', _('Пуговица')),
        ('QC', _('Контроль качества')),
    )
    STATUS_CHOICES = (
        ('READY', _('Готово к работе')),
        ('COMPLETED', _('Завершено')), 
        ('CONFIRMED', _('Подтверждено')), 
    )

    batch_product = models.ForeignKey(BatchProduct, on_delete=models.CASCADE, related_name='stages', verbose_name=_('Товар в партии'))
    stage_type = models.CharField(max_length=20, choices=STAGE_CHOICES, verbose_name=_('Тип этапа'))
    assigned_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('Ответственный/Исполнитель'),
        related_name='assigned_process_stages'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PLANNED', verbose_name=_('Статус'))
    start_date = models.DateTimeField(null=True, blank=True, verbose_name=_('Дата Начала'))
    end_date = models.DateTimeField(null=True, blank=True, verbose_name=_('Дата Окончания'))

   

    # Aggregate quantity completed in this stage (calculated from WorkLogs)
    quantity_completed = models.PositiveIntegerField(
        default=0,  
        verbose_name=_('Выполнено Итого (выход)')
    )

    # Aggregate quantity found defective in this stage (calculated from WorkLogs)
    quantity_deffect = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Брак Итого (на этом этапе)')
    )


    confirmed_by = models.ForeignKey(
        User,
        related_name='confirmed_stages',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_('Подтвердил')
    )
    confirmed_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Дата подтверждения'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания записи этапа'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Обновлено'))
    close_session = models.BooleanField(default=False, verbose_name=_('Сессия закрыта (Работа завершена)')) # Clarified verbose name

    def __str__(self):
        stage_display = self.get_stage_type_display()
        batch_product_str = str(self.batch_product) if self.batch_product else _("N/A BatchProduct")
        status_display = self.get_status_display()
        return f"{stage_display} - {batch_product_str} ({status_display})"


    # def get_expected_input_quantity(self):
    #     """Returns the completed quantity from the previous stage, if any."""
    #     if self.previous_stage:
    #         # Ensure previous stage data is fresh if needed
    #         # self.previous_stage.refresh_from_db(fields=['quantity_completed'])
    #         return self.previous_stage.quantity_completed
    #     return 0 # First stage starts with 0 input from previous

    # def save(self, *args, **kwargs):
    #     # Automatically set input quantity based on previous stage ONLY when created
    #     # and if previous_stage is already set. Avoids overriding later manual changes.
    #     is_new = self.pk is None
    #     if is_new and self.previous_stage and self.quantity_input == 0:
    #          self.quantity_input = self.get_expected_input_quantity()
    #     super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Этап процесса")
        verbose_name_plural = _("Этапы процессов")
        ordering = ['batch_product__batch__batch_number', 'batch_product__product__title', 'created_at']


class WorkLog(models.Model):
    stage = models.ForeignKey(
        ProcessStage,
        on_delete=models.CASCADE,
        related_name='work_logs',
        verbose_name=_('Этап процесса')
    )
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT, 
        related_name='work_logs',
        verbose_name=_('Сотрудник')
    )
    quantity_processed = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Обработано штук (за эту запись)')
    )
    quantity_defective = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Обнаружено брака (за эту запись)')
    )
    log_time = models.DateTimeField(
        default=timezone.now, 
        verbose_name=_('Время записи лога')
    )
    notes = models.TextField(blank=True, null=True, verbose_name=_('Примечания'))
    created_at = models.DateTimeField(auto_now_add=True, null=True, verbose_name='Дата Создание')
    def __str__(self):
        user_name = self.user.get_full_name() or self.user.username
        return f"{user_name} - {self.stage} - Qty: {self.quantity_processed} (Def: {self.quantity_defective}) @ {self.log_time.strftime('%Y-%m-%d %H:%M')}"

    def clean(self):
        """
        Add validation here if needed, e.g., ensure processed >= defective.
        More complex validation (not exceeding stage limits) is better done
        in the form or view that creates the WorkLog.
        """
        if self.quantity_defective > self.quantity_processed:
            raise ValidationError(_('Количество брака не может превышать количество обработанных.'))

    class Meta:
        verbose_name = _("Запись о выполненной работе")
        verbose_name_plural = _("Записи о выполненной работе")