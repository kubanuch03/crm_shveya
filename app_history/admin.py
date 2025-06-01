from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import AdminHistoryLog


@admin.register(AdminHistoryLog)
class AdminHistoryLogAdmin(ModelAdmin):
    
    list_display = ['status', 'title', 'format_created_at']

    def format_created_at(self, obj):
        return obj.created_at.strftime("%Y-%m-%d %H:%M")
    format_created_at.short_description = 'Дата Создание'

