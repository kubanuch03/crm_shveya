from django.conf import settings
from app_global.models import PackagingSettings, TailorSettings, UtugSettings, CroiSettings
from django.core.management.base import BaseCommand
from abc import ABC, abstractmethod








class SettingsFactory:
    """Фабрика для создания объектов настроек"""

    settings_map = {
        "packaging": PackagingSettings,
        "tailor": TailorSettings,
        "utug": UtugSettings,
        "croi": CroiSettings
    }

    @classmethod
    def create_all(cls):
        """Создаёт объекты или обновляет per_unit, если уже существует"""
        created_objects = {}
        for key, model_class in cls.settings_map.items():
            per_unit_value = cls.default_values.get(key, 0.0)
            obj, created = model_class.objects.get_or_create()
            if not created:
                obj.per_unit = per_unit_value
                obj.save()
            created_objects[key] = obj
        return created_objects




        