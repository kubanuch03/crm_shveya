from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import AdminHistoryLog


@receiver(post_save, sender=AdminHistoryLog)
def limit_log_admin(sender, instance, created, **kwargs):
    # max_log = GlobalSettings.objec
    max_log = 1000
    total_logs = AdminHistoryLog.objects.count()
    if total_logs> max_log:
        total_logs = AdminHistoryLog.objects.earliest("created_at").delete()

