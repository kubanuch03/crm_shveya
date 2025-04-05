from django.contrib import admin
from .models import Logistics
from unfold.admin import ModelAdmin

# Register your models here.

@admin.register(Logistics)
class LogisticsAdmin(ModelAdmin):
    list_display = ['send_user', 'title', 'address', 'send_date', ]
    list_links = ['send_user', 'title', 'address', 'send_date', ]
    search_fields = ['send_user__username','send_user__first_name', 'send_user__last_name', 'title', ]

    readonly_fields = (
        "created_at",

    )

    fieldsets = [
        (
            'Процесс Упаковки',
            {
                "fields": (
                    # "id", 
                    "send_user", 
                    'title', 
                    'description', 
                    "address", 
                    'send_date', 
                    "product",
                    "created_at",
                    ),
            },
        ),
        
    ]