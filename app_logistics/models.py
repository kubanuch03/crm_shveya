from django.db import models
from app_users.models import User
from app_productions.models import Product

class Logistics(models.Model):
    title = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(blank=True, null=True,verbose_name='Описание')
    address = models.CharField(max_length=255, blank=True, null=True)
    send_date = models.DateTimeField(blank=True, null=True,auto_now_add=False)
    send_user = models.ForeignKey(User, blank=True, null=True,on_delete=models.SET_NULL, verbose_name='Кто отправил')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создание')
    product = models.ManyToManyField(Product, verbose_name='Товары')
    def __str__(self):
        return f"{self.title}"

    class Meta:
        verbose_name = "Логистика(Карго)"
        verbose_name_plural = "Логистика(Карго)"

