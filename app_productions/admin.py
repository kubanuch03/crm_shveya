from django.contrib import admin
from .models import Product, Color, Size, Product_Model, Category
from unfold.admin import ModelAdmin
from .models import ProductionBatch, ProcessStage, BatchProduct, Product, Color, Size, Product_Model, Category

class ProductionBatchAdmin(ModelAdmin):
    list_display = ['batch_number','title', 'planned_completion_date', 'notes', 'is_completed', 'created_at']
    list_display_links = ['batch_number', 'title','created_at']
    readonly_fields = [
        "created_at",
    ]
    fieldsets = (
        (
            "Производственные Партии",
            {
                "fields": (
                    # "FaceEvent_preview",
                    # "id",
                    "batch_number",
                    "title",
                    "planned_completion_date",
                    "notes",
                    "is_completed",
                    
                    "created_at",
                )
            },
        ),
    )

class BatchProductAdmin(ModelAdmin):
    list_display = ['batch','product',]
    list_display_links = ['batch','product']
  
    fieldsets = (
        (
            "Производственные Партии",
            {
                "fields": (
                    # "FaceEvent_preview",
                    # "id",
                    "batch",
                    "product",
                )
            },
        ),
    )

class ProcessStageAdmin(ModelAdmin):
    list_display = ['batch_product','stage_type', 
                    'assigned_user','status','start_date','end_date',
                    'quantity_completed','quantity_defective','previous_stage', 
                    'confirmed_by','confirmed_at'
                    ]
    list_display_links = ['batch_product','stage_type', 
                    'assigned_user','status','start_date','end_date',
                    'quantity_completed','quantity_defective','previous_stage', 
                    'confirmed_by','confirmed_at', 
                    ]
    readonly_fields = [
        "created_at",
        "updated_at",
    ]
    search_fields = ['batch_product__batch__batch_number', 'batch_product__product__title']
    fieldsets = (
        (
            "Производственные Партии",
            {
                "fields": (
                    'batch_product','stage_type', 
                    'assigned_user','status','start_date','end_date',
                    'quantity_completed','quantity_defective','previous_stage', 
                    'confirmed_by','confirmed_at','created_at', 'updated_at',
                )
            },
        ),
    )

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
    list_display = ['id','title', 'quentity','remains', 'created_at']
    list_display_links = ['id','title', 'quentity', 'remains', 'created_at']

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
                    "remains",
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
admin.site.register(ProductionBatch, ProductionBatchAdmin)
admin.site.register(BatchProduct, BatchProductAdmin)
admin.site.register(ProcessStage, ProcessStageAdmin)
admin.site.register(Size, SizeAdmin)
admin.site.register(Color, ColorAdmin)
admin.site.register(Product_Model, ProductModelAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)

