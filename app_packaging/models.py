from django.db import models
from app_productions.models import Product


class Productprocess(models.Model):
    title = models.CharField(max_length=255, verbose_name='Название')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создание')
    start_date = models.DateField(blank=True, null=True, verbose_name='дата Начала')
    end_date = models.DateField(blank=True, null=True, verbose_name='дата Окончание')
    packed = models.PositiveIntegerField(default=0, verbose_name='Упаковано')
    send_cargo = models.PositiveIntegerField(default=0, verbose_name='Отправлено в Карго')
    marriage = models.PositiveIntegerField(default=0, verbose_name='Брак')

    product = models.ManyToManyField(Product, blank=True, null=True, on_delete=models.SET_NULL, verbose_name='Товар')

    def __str__(self):
        return f"{self.title}"

    class Meta:
        verbose_name = "Производственный Процесс"
        verbose_name_plural = "Производственный Процесс"
