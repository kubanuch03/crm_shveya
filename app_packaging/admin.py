from django.contrib import admin
from .models import ProductProcess
from unfold.admin import ModelAdmin

# Register your models here.

@admin.register(ProductProcess)
class ProductProcessAdmin(ModelAdmin):
    list_display = ['packer', 'title', 'packed', 'send_cargo', 'marriage', 'start_date', 'end_date', 'confirmed', ]
    list_links = ['packer', 'title', 'packed', 'send_cargo', 'marriage', 'start_date', 'end_date', ]
    search_fields = ['packer__username','packer__first_name', 'packer__last_name', 'title', 'packed', ]

    readonly_fields = (
        "created_at",

    )

    fieldsets = [
        (
            'Процесс Упаковки',
            {
                "fields": (
                    # "id", 
                    "packer", 
                    'title', 
                    'start_date', 
                    "end_date", 
                    'packed', 
                    "send_cargo", 
                    "marriage", 
                    "product",
                    "confirmed",
                    "created_at",
                    ),
            },
        ),
        
    ]