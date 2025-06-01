from django.contrib import admin
from .models import Croi
from unfold.admin import ModelAdmin

# Register your models here.

@admin.register(Croi)
class CroiProcessAdmin(ModelAdmin):
    list_display = ['user', 'title', 'quentity_detail', 'finish', 'created_at', ]
    list_links = ['user', 'title', 'quentity_detail', 'finish', 'created_at', ]
    search_fields = ['user__username','user__first_name', 'user__last_name', 'title' ]

    readonly_fields = (
        "created_at",

    )

    fieldsets = [
        (
            'Процесс Крой',
            {
                "fields": (
                    # "id", 
                    "user", 
                    'title', 
                    'quentity_detail', 
                    "created_at",
                    ),
            },
        ),
        
    ]