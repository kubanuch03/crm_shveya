# app_global/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from decimal import Decimal # <<< ДОБАВИТЬ ИМПОРТ

class PackagingSettings(models.Model):
    title = models.CharField(max_length=255, verbose_name='Наименование')
    per_unit = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name='За единицу') # ИЗМЕНЕНИЕ
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создание')
    def __str__(self): return f'{self.title}'
    class Meta: verbose_name = 'Настройка Упаковки'; verbose_name_plural = 'Настройка Упаковки'

class UtugSettings(models.Model):
    title = models.CharField(max_length=255, verbose_name='Наименование')
    per_unit = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name='За единицу') # ИЗМЕНЕНИЕ
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создание')
    def __str__(self): return f'{self.title}'
    class Meta: verbose_name = 'Настройка Утюга'; verbose_name_plural = 'Настройка Утюга'

class TailorSettings(models.Model): # Для SEWING
    title = models.CharField(max_length=255, verbose_name='Наименование')
    per_unit = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name='За единицу') # ИЗМЕНЕНИЕ
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создание')
    def __str__(self): return f'{self.title}'
    class Meta: verbose_name = 'Настройка Шитья'; verbose_name_plural = 'Настройка Шитья'

class CroiSettings(models.Model): # Для CUTTING
    title = models.CharField(max_length=255, verbose_name='Наименование')
    per_unit = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name='За единицу') # ИЗМЕНЕНИЕ
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создание')
    def __str__(self): return f'{self.title}'
    class Meta: verbose_name = 'Настройка Крой'; verbose_name_plural = 'Настройка Крой'

# Добавь аналогично ButtonsSettings, QCSettings, если для них есть глобальные ставки