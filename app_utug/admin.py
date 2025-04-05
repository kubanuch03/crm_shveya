from django.contrib import admin
from .models import UtugProcess
from unfold.admin import ModelAdmin

# Register your models here.

@admin.register(UtugProcess)
class UtugProcessAdmin(ModelAdmin):
    list_display = ['utujnik', 'title', 'done', 'marriage', 'start_date', 'end_date', 'confirmed', ]
    list_links = ['utujnik', 'title', 'done', 'send_cargo', 'marriage', 'start_date', 'end_date', ]
    search_fields = ['utujnik__username','utujnik__first_name', 'utujnik__last_name', 'title', 'done', ]

    readonly_fields = (
        "created_at",

    )

    fieldsets = [
        (
            'Процесс Утюга',
            {
                "fields": (
                    # "id", 
                    "utujnik", 
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