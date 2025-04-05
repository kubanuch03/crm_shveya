from django.db import models
from app_productions.models import Product
from app_users.models import User


class UtugProcess(models.Model):
    title = models.CharField(max_length=255, verbose_name='Наименование')
    utujnik = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Утюжник')
    start_date = models.DateField(blank=True, null=True, verbose_name='Дата Начала')
    end_date = models.DateField(blank=True, null=True, verbose_name='Дата Окончание')
    done = models.PositiveIntegerField(default=0, blank=True, null=True, verbose_name='Утюжано')
    marriage = models.PositiveIntegerField(default=0, blank=True, null=True, verbose_name='Брак')

    product = models.ManyToManyField(Product, blank=True, verbose_name='Товар')
    confirmed = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE,related_name='confirmed_utug', verbose_name='Подтвердил')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создание')

    def __str__(self):
        return f"{self.title}"