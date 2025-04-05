from django.db import models
from app_productions.models import Product
from app_users.models import User

class ProductProcess(models.Model):
    packer = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Упаковщик')
    title = models.CharField(max_length=255, verbose_name='Название')
    start_date = models.DateField(blank=True, null=True, verbose_name='Дата Начала')
    end_date = models.DateField(blank=True, null=True, verbose_name='Дата Окончание')
    packed = models.PositiveIntegerField(default=0, blank=True, null=True, verbose_name='Упаковано')
    send_cargo = models.PositiveIntegerField(default=0, blank=True, null=True, verbose_name='Отправлено в Карго')
    marriage = models.PositiveIntegerField(default=0, blank=True, null=True, verbose_name='Брак')

    product = models.ManyToManyField(Product, blank=True, verbose_name='Товар')
    confirmed = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE,related_name='confirmed', verbose_name='Подтвердил')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создание')


    def __str__(self):
        return f"Название: {self.title} Упаковщик: {self.packer}"

    class Meta:
        verbose_name = "Процесс Упаковки"
        verbose_name_plural = "Процесс Упаковки"


