from django.contrib import admin
from .models import TailorProcess
from unfold.admin import ModelAdmin


@admin.register(TailorProcess)
class TailorProcessAdmin(ModelAdmin):
    list_display = ['tailor', 'title', 'done', 'marriage', 'start_date', 'end_date', 'confirmed', ]
    list_links = ['tailor', 'title', 'done', 'send_cargo', 'marriage', 'start_date', 'end_date', ]
    search_fields = ['tailor__username','tailor__first_name', 'tailor__last_name', 'title', 'done', ]

    readonly_fields = (
        "created_at",

    )

    fieldsets = [
        (
            'Процесс Упаковки',
            {
                "fields": (
                    # "id", 
                    "tailor", 
                    'title', 
                    'start_date', 
                    "end_date", 
                    'done', 
                    "marriage", 
                    "product",
                    "confirmed",
                    "created_at",
                    ),
            },
        ),
        
    ]