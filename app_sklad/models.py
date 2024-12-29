from django.db import models
from app_productions.models import Product



class CategorySklad(models.Model):
    title = models.CharField(max_length=255, verbose_name='Название')
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        verbose_name = _("Категория Склада")
        verbose_name_plural = _("Категория Склада")

    def __str__(self):
        return f"{self.title}"
    
class Sklad(models.Model):
    title = models.CharField(max_length=255, verbose_name='Название')
    created_at = models.DateTimeField(auto_now_add=True)
    category_sklad = models.ManyToManyField(CategorySklad, verbose_name='Категория склада')

    class Meta:
        verbose_name = _("Склад")
        verbose_name_plural = _("Склад")

    def __str__(self):
        return f"{self.title}"