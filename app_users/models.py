from django.db import models
from django.contrib.auth.models import AbstractUser, Permission
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Group


from .managers import CustomUserManager


class Filial(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.title}"

class User(AbstractUser):
    username = models.CharField(unique=True,max_length=255, verbose_name='Псевдоним')
    email = models.EmailField(blank=True,null=True,max_length=255, verbose_name='Почта')
    image = models.ImageField(
        upload_to="images/employees/%Y/%m/%d/", null=True, blank=True, verbose_name="Фото"
    )
    groups = models.ManyToManyField(Group, blank=True)
    first_name = models.CharField(max_length=255, verbose_name='Имя')
    last_name = models.CharField(max_length=255, verbose_name='Фамилия')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создание')
    modified_at = models.DateTimeField(auto_now=True, verbose_name='Тзменено')
    uuid = models.CharField(unique=True, blank=True, null=True, verbose_name='UUiD')

    phone_number = models.CharField(max_length=14, blank=True, null=True, verbose_name='Номер Телефона')
    telegram = models.CharField(max_length=255, blank=True, null=True, verbose_name='Телеграм')
    whatsapp = models.CharField(max_length=255, blank=True, null=True, verbose_name='WhatsApp')
    
    filial = models.ForeignKey(Filial,null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Филиал')

    access_token = models.CharField(max_length=255, null=True, blank=True)
    refresh_token = models.CharField(max_length=255, blank=True, null=True)


    is_superuser = models.BooleanField(default=False, verbose_name='Супер пользователь')
    is_active = models.BooleanField(default=False, verbose_name='Активный')
    is_technolog = models.BooleanField(default=False, verbose_name="Технолог")
    is_upakovka = models.BooleanField(default=False, verbose_name="Упаковка")
    is_utug = models.BooleanField(default=False, verbose_name="Утюг")
    is_croi = models.BooleanField(default=False, verbose_name="Крой")
    is_buttons = models.BooleanField(default=False, verbose_name="Пуговица") 
    is_tailor = models.BooleanField(default=False, verbose_name="Портной") # тигуучу
    is_povar = models.BooleanField(default=False, verbose_name="Повар")

    EMAIL_FIELD = ['username']
    groups = models.ManyToManyField(
        'auth.Group', 
        related_name='custom_user_set', 
        blank=True, 
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission', 
        related_name='custom_user_permissions', 
        blank=True, 
        verbose_name='user permissions'
    )

    objects = CustomUserManager()


    class Meta:
        db_table = "users"
        verbose_name = _("Пользователь")
        verbose_name_plural = _("Пользователи")

    def __str__(self):
        return self.username



