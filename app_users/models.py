from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


from .managers import CustomUserManager


class User(AbstractUser):
    username = models.CharField(unique=True,max_length=255)
    email = models.EmailField(blank=True,null=True,max_length=255)
    image = models.ImageField(
        upload_to="images/employees/%Y/%m/%d/", null=True, blank=True, verbose_name="Image"
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    modified_at = models.DateTimeField(_("modified at"), auto_now=True)
    uuid = models.CharField(unique=True, blank=True, null=True)


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
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return self.username
