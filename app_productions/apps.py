from django.apps import AppConfig


class AppProductionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_productions'
    verbose_name = 'Производство'

    def ready(self):
        import app_productions.signals