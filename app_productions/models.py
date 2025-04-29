from django.db import models, transaction
from app_users.models import User
from django.db.models import F
from django.utils.translation import gettext_lazy as _ # Import gettext_lazy

# Assuming logger is configured elsewhere
# from logger import logger

class Color(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Название')) # Use translation
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создание'))

    def __str__(self):
        return f"{self.title}" if self.title else f"Color {self.id}"

    class Meta:
        verbose_name = _("Цвет Товара")
        verbose_name_plural = _("Цвет Товара")
        ordering = ['title'] # Add default ordering

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
        verbose_name = _("Модель Товара") # Changed from Брэнд for clarity
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

    # Removed the save method that referred to non-existent fields
    # def save(self, *args, **kwargs):
    #     if self.pk is None  and self.remains is None:
    #         self.remains = self.quentity
    #     super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Товар")
        verbose_name_plural = _("Товары")
        ordering = ['title']


class ProductionBatch(models.Model):
    batch_number = models.CharField(max_length=100, unique=True, blank=True, null=True, verbose_name=_('Номер партии'))
    title = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('Наименование')) 
    planned_completion_date = models.DateField(null=True, blank=True, verbose_name=_('Плановая дата завершения'))
    notes = models.TextField(blank=True, null=True, verbose_name=_('Примечания'))
    is_completed = models.BooleanField(default=False, verbose_name=_('Партия завершена'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))
    # Add Filial here if needed for filtering
    # filial = models.ForeignKey('your_filial_app.Filial', null=True, blank=True, on_delete=models.SET_NULL, verbose_name=_('Филиал'))


    def __str__(self):
        return f"№:{self.batch_number} {self.title or ''}".strip()

    class Meta:
        verbose_name = _("Производственная партия")
        verbose_name_plural = _("Производственные партии")
        ordering = ['-created_at'] # Order by most recent first

class BatchProduct(models.Model):
    batch = models.ForeignKey(ProductionBatch, related_name='products_in_batch', on_delete=models.CASCADE, verbose_name=_('Партия'))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_('Товар'))
    # Removed planned_quantity - add back if needed
    quantity_finish = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Количество Готово (факт)'),
        help_text=_('Итоговое количество после завершения всех этапов')
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
        ('Utug', _('Утюг')), 
        ('PACKING', _('Упаковка')),
        ('CUTTING', _('Крой')),
        ('BUTTONS', _('Пуговица')), 
        ('QC', _('Контроль качества')),
    )
    STATUS_CHOICES = (
        ('PLANNED', _('Запланировано')),
        ('IN_PROGRESS', _('В работе')),
        ('COMPLETED', _('Завершено')),
        ('CONFIRMED', _('Подтверждено')),
        ('CANCELLED', _('Отменено')),
    )

    batch_product = models.ForeignKey(BatchProduct, on_delete=models.CASCADE, related_name='stages', verbose_name=_('Товар в партии'))
    stage_type = models.CharField(max_length=20, choices=STAGE_CHOICES, verbose_name=_('Тип этапа'))
    assigned_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('Исполнитель'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PLANNED', verbose_name=_('Статус'))

    start_date = models.DateTimeField(null=True, blank=True, verbose_name=_('Дата Начала'))
    end_date = models.DateTimeField(null=True, blank=True, verbose_name=_('Дата Окончания'))

    quantity_completed = models.PositiveIntegerField(default=0, verbose_name=_('Выполнено (выход)'))
    quantity_defective = models.PositiveIntegerField(default=0, verbose_name=_('Брак (на этом этапе)'))
    previous_stage = models.OneToOneField(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='next_stage',
        verbose_name=_('Предыдущий этап')
    )

    confirmed_by = models.ForeignKey(User, related_name='confirmed_stages', null=True, blank=True, on_delete=models.SET_NULL, verbose_name=_('Подтвердил'))
    confirmed_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Дата подтверждения'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания записи этапа'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Обновлено'))
    close_session = models.BooleanField(default=False, verbose_name=_('Сессия закрыта')) # Added translation


    def __str__(self):
        stage_display = self.get_stage_type_display()
        batch_product_str = str(self.batch_product) if self.batch_product else _("N/A BatchProduct")
        status_display = self.get_status_display()
        return f"{stage_display} - {batch_product_str} ({status_display})"


 
    class Meta:
        verbose_name = _("Этап процесса")
        verbose_name_plural = _("Этапы процессов")
        ordering = ['batch_product__batch__batch_number', 'batch_product__product__title', 'created_at']