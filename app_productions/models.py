from django.db import models, transaction
from app_users.models import User
from django.db.models import F

from logger import logger

class Color(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True, verbose_name='Название')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создание')

    def __str__(self):
        return f"{self.title}"
    
    class Meta:
        verbose_name = "Цвет Товара"
        verbose_name_plural = "Цвет Товара"

class Size(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True, verbose_name='Название')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создание')

    def __str__(self):
        return f"{self.title}"
    
    class Meta:
        verbose_name = "Размер Товара"
        verbose_name_plural = "Размер Товара"

class Category(models.Model):
    title = models.CharField(max_length=255, verbose_name='Название')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создание')

    def __str__(self):
        return f"{self.title}"
    
    class Meta:
        verbose_name = "Категория Товара"
        verbose_name_plural = "Категория Товара"

class Product_Model(models.Model):
    title = models.CharField(max_length=255, verbose_name='Название')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создание')

    def __str__(self):
        return f"{self.title}"
    
    class Meta:
        verbose_name = "Брэнд Товара"
        verbose_name_plural = "Брэнд Товара"

class Product(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True, verbose_name='Название')
    quentity = models.PositiveIntegerField(default=0, blank=True, null=True, verbose_name='Кол-во')
    color = models.ManyToManyField(Color, blank=True, verbose_name='Цвет')
    size = models.ManyToManyField(Size, blank=True, verbose_name='Размер ')
    category = models.ManyToManyField(Category, blank=True, verbose_name='Категория')
    product_model = models.ManyToManyField(Product_Model, blank=True, verbose_name='Модель')
    remains = models.PositiveIntegerField(blank=True, null=True, verbose_name='Осталось произвести')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создание')



    def __str__(self):
        return f"{self.title}"
    def save(self, *args, **kwargs):
        if self.pk is None  and self.remains is None:
            self.remains = self.quentity
        super().save(*args, **kwargs)
    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товар"


class ProductionBatch(models.Model):
    """ Производственная партия/заказ """
    batch_number = models.CharField(max_length=100, unique=True, verbose_name='Номер партии')
    title = models.CharField(max_length=100, blank=True, null=True, unique=True, verbose_name='Наименование')
    # order = models.ForeignKey(Order, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Заказ клиента')
    planned_completion_date = models.DateField(null=True, blank=True, verbose_name='Плановая дата завершения')
    notes = models.TextField(blank=True, null=True, verbose_name='Примечания')
    is_completed = models.BooleanField(default=False, verbose_name='Партия завершена') 
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    def __str__(self):
        return f"№:{self.batch_number} {self.title}"

    class Meta:
        verbose_name = "Производственная партия"
        verbose_name_plural = "Производственные партии"

class BatchProduct(models.Model):
    """ Товары, входящие в партию, и их плановое количество """
    batch = models.ForeignKey(ProductionBatch, related_name='products_in_batch', on_delete=models.CASCADE, verbose_name='Партия')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар') 
    # planned_quantity = models.PositiveIntegerField(verbose_name='Плановое количество')
    quantity_finish = models.PositiveIntegerField(
        default=0,
        verbose_name='Количество Готово (факт)',
        help_text='Итоговое количество после завершения всех этапов'
    )

    def __str__(self):
        return f"{self.product.title} - (Партия: {self.batch.batch_number})" 

    class Meta:
        unique_together = ('batch', 'product') 
        verbose_name = "Товар в партии"
        verbose_name_plural = "Товары в партии"


class ProcessStage(models.Model):
    """ Этап производственного процесса для конкретного товара в партии """
    STAGE_CHOICES = (
        ('SEWING', 'Шитье'),
        ('Utug', 'Утюг'),
        ('PACKING', 'Упаковка'),
        ('CUTTING', 'Крой'), 
        ('QC', 'Контроль качества'), 
    )
    STATUS_CHOICES = (
        ('PLANNED', 'Запланировано'),
        ('IN_PROGRESS', 'В работе'),
        ('COMPLETED', 'Завершено'),
        ('CONFIRMED', 'Подтверждено'),
        ('CANCELLED', 'Отменено'),
    )

    batch_product = models.ForeignKey(BatchProduct, on_delete=models.CASCADE, related_name='stages', verbose_name='Товар в партии')
    stage_type = models.CharField(max_length=20, choices=STAGE_CHOICES, verbose_name='Тип этапа')
    assigned_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Исполнитель')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PLANNED', verbose_name='Статус')

    start_date = models.DateTimeField(null=True, blank=True, verbose_name='Дата Начала')
    end_date = models.DateTimeField(null=True, blank=True, verbose_name='Дата Окончания')

    quantity_completed = models.PositiveIntegerField(default=0, verbose_name='Выполнено (выход)')
    quantity_defective = models.PositiveIntegerField(default=0, verbose_name='Брак (на этом этапе)')
    previous_stage = models.OneToOneField(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='next_stage',
        verbose_name='Предыдущий этап'
    )

    confirmed_by = models.ForeignKey(User, related_name='confirmed_stages', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Подтвердил')
    confirmed_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата подтверждения')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания записи этапа')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')
    close_session = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.get_stage_type_display()} - {self.batch_product} ({self.status})"


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return f"{self.get_stage_type_display()} - {self.batch_product} ({self.status})"

    def save(self, *args, **kwargs):
        

        super().save(*args, **kwargs)

                

               


    class Meta:
        verbose_name = "Этап процесса"
        verbose_name_plural = "Этапы процессов"
        ordering = ['batch_product__batch__batch_number', 'batch_product__product__title', 'created_at']




# class Cargo(models.Model):
#     title = models.CharField(max_length=255)
#     coming = models.DateTimeField()

