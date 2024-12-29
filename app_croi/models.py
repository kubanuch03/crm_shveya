from django.db import models
from app_users.models import User
from django.utils.translation import gettext_lazy as _



class Croi(models.Model):
    title = models.CharField(max_length=255, verbose_name='Модель Изделий')
    quentity_detail = models.PositiveIntegerField(default=0, verbose_name='Количество Изделий')
    finish = models.DateField(blank=True, null=True, verbose_name='дата завершения')
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, verbose_name='Ответсвенный Кройщик')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _("Крой")
        verbose_name_plural = _("Крой")

    def __str__(self):
        return f"{self.title}"