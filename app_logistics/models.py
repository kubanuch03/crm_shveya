from django.db import models
from app_users.models import User


class Logistics(models.Model):
    title = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(blank=True, null=True,verbose_name='Описание')
    address = models.CharField(max_length=255, blank=True, null=True)
    send_date = models.DateTimeField(blank=True, null=True,auto_now_add=False)
    send_user = models.ForeignKey(User, blank=True, null=True,on_delete=models.SET_NULL)


    def __str__(self):
        return f"{self.title}"

    class Meta:
        verbose_name = "Логистика"
        verbose_name_plural = "Логистика"

