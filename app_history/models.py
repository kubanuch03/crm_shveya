from django.db import models
from django.utils.translation import gettext_lazy as _

from app_users.models import User

STATUS_CHOICE = (
    ('INFO', "INFO"),
    ('ERROR', "ERROR"),
    ('WARNING', "WARNING"),
)

class AdminHistoryLog(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True, verbose_name='Наименование')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, verbose_name='Пользователь')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создание')
    status = models.CharField(choices=STATUS_CHOICE, blank=True, null=True, default='INFO', verbose_name='Статус')

    def __str__(self):
        return f"{self.title} {self.created_at}"
    

    class Meta:
        verbose_name = _("История Логов")
        verbose_name_plural = _("Истории Логов")