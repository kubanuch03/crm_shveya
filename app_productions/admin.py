from django.contrib import admin
from .models import Product, Color, Size, Product_Model, Category
from unfold.admin import ModelAdmin




class ColorAdmin(ModelAdmin):
    list_display = ['id','title','created_at']
    list_display_links = ['id','title','created_at']

    search_fields = ("title",)
    ordering = ("-id",)
    readonly_fields = [
        "created_at",
    ]
    fieldsets = (
        (
            "Цвет",
            {
                "fields": (
                    # "FaceEvent_preview",
                    # "id",
                    "title",
                    
                    "created_at",
                )
            },
        ),
    )

class SizeAdmin(ModelAdmin):
    list_display = ['id','title','created_at']
    list_display_links = ['id','title','created_at']

    search_fields = ("title",)
    ordering = ("-id",)
    readonly_fields = [
        "created_at",
    ]
    fieldsets = (
        (
            "Цвет",
            {
                "fields": (
                    # "FaceEvent_preview",
                    # "id",
                    "title",
                    
                    "created_at",
                )
            },
        ),
    )

class ProductModelAdmin(ModelAdmin):
    list_display = ['id','title','created_at']
    list_display_links = ['id','title','created_at']

    search_fields = ("title",)
    ordering = ("-id",)
    readonly_fields = [
        "created_at",
    ]
    fieldsets = (
        (
            "Цвет",
            {
                "fields": (
                    
                    "title",
                    
                    "created_at",
                )
            },
        ),
    )

class CategoryAdmin(ModelAdmin):
    list_display = ['id','title','created_at']
    list_display_links = ['id','title','created_at']

    search_fields = ("title",)
    ordering = ("-id",)
    readonly_fields = [
        "created_at",
    ]
    fieldsets = (
        (
            "Категория",
            {
                "fields": (
                    
                    "title",
                    
                    "created_at",
                )
            },
        ),
    )

class ProductAdmin(ModelAdmin):
    list_display = ['id','title', 'quentity', 'price','created_at']
    list_display_links = ['id','title', 'quentity', 'price','created_at']

    search_fields = ("title",)
    ordering = ("-id",)
    readonly_fields = [
        "created_at",
    ]
    fieldsets = (
        (
            "Товар",
            {
                "fields": (
                    
                    "title",
                    "quentity",
                    "price",
                    "created_at",
                )
            },
        ),
        (
            "Дополнительно",
            {
                "fields": (
                    "color",
                    "size",
                    "category",
                    "product_model",
                )
            }
        )
    )
admin.site.register(Color, ColorAdmin)
admin.site.register(Size, SizeAdmin)
admin.site.register(Product_Model, ProductModelAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)

