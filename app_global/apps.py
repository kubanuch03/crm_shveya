from django.apps import AppConfig


class AppGlobalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_global'
    verbose_name = 'Глобальные Настройки'
