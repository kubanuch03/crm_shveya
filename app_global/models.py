from django.db import models




class PackagingSettings(models.Model):
    title = models.CharField(max_length=255, verbose_name='Наименование')
    per_unit = models.PositiveIntegerField(verbose_name='За единицу')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создание')

    def __str__(self):
        return f'{self.title}'
    class Meta:
        verbose_name = 'Настройка Упаковки'
        verbose_name_plural = 'Настройка Упаковки'


class UtugSettings(models.Model):
    title = models.CharField(max_length=255, verbose_name='Наименование')
    per_unit = models.PositiveIntegerField(verbose_name='За единицу')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создание')

    def __str__(self):
        return f'{self.title}'
    class Meta:
        verbose_name = 'Настройка Утюга'
        verbose_name_plural = 'Настройка Утюга'

class TailorSettings(models.Model):
    title = models.CharField(max_length=255, verbose_name='Наименование')
    per_unit = models.PositiveIntegerField(verbose_name='За единицу')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создание')

    def __str__(self):
        return f'{self.title}'
    class Meta:
        verbose_name = 'Настройка Шитья'
        verbose_name_plural = 'Настройка Шитья'

class CroiSettings(models.Model):
    title = models.CharField(max_length=255, verbose_name='Наименование')
    per_unit = models.PositiveIntegerField(verbose_name='За единицу')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создание')

    def __str__(self):
        return f'{self.title}'
    class Meta:
        verbose_name = 'Настройка Крой'
        verbose_name_plural = 'Настройка Крой'