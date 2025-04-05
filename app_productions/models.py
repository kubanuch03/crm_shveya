from django.db import models
from app_users.models import User


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
    price = models.PositiveIntegerField(null=True, blank=True,verbose_name='Цена')

    color = models.ManyToManyField(Color, blank=True, verbose_name='Цвет')
    size = models.ManyToManyField(Size, blank=True, verbose_name='Размер  ')
    category = models.ManyToManyField(Category, blank=True, verbose_name='Категория')
    product_model = models.ManyToManyField(Product_Model, blank=True, verbose_name='Модель')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создание')


    def __str__(self):
        return f"{self.title}"
    
    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товар"


class Cargo(models.Model):
    title = models.CharField(max_length=255)
    coming = models.DateTimeField()


