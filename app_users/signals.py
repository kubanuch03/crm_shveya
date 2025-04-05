from django.db.models.signals import post_save
from django.dispatch import receiver
from app_users.models import User
from app_history.models import AdminHistoryLog
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("User signal")





@receiver(post_save, sender=User)
def log_admin_action(sender, instance, created, **kwargs):
    if created:
        title = f"Создан Новый пользовать Username: {instance.username} Имя: {instance.first_name}"
    else:
        title = f"Информация о пользователе обновлен {instance.username} {instance.first_name}"    
    AdminHistoryLog.objects.create(user=instance, title=title)
    logger.info(title)
