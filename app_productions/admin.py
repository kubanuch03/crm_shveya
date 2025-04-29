from django.contrib import admin
# Use ModelAdmin from unfold consistently
from unfold.admin import ModelAdmin
from django.utils.translation import gettext_lazy as _

# Import your models from the current app (.)
from .models import (
    ProductionBatch, ProcessStage, BatchProduct, Product,
    Color, Size, Product_Model, Category
)
# Import User model (adjust path if it's in a different app)
from app_users.models import User


# --- Admin for related models (ensure they have search_fields if used in autocomplete) ---

# Assuming CustomUserAdmin is defined in app_users/admin.py and has search_fields
# If not, you need a basic definition here or there:
# from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# @admin.register(User)
# class CustomUserAdmin(BaseUserAdmin):
#     search_fields = ('username', 'first_name', 'last_name', 'email')
#     # ... other user admin configurations ...


@admin.register(Color)
class ColorAdmin(ModelAdmin):
    list_display = ['id', 'title', 'created_at']
    list_display_links = ['id', 'title']
    search_fields = ("title",)
    ordering = ("-created_at",) # Order by creation date usually makes more sense
    readonly_fields = ["created_at"]
    fieldsets = (
        (None, {"fields": ("title", "created_at")}), # Simpler fieldset title
    )

@admin.register(Size)
class SizeAdmin(ModelAdmin):
    list_display = ['id', 'title', 'created_at']
    list_display_links = ['id', 'title']
    search_fields = ("title",)
    ordering = ("-created_at",)
    readonly_fields = ["created_at"]
    fieldsets = (
        (None, {"fields": ("title", "created_at")}),
    )

@admin.register(Product_Model)
class ProductModelAdmin(ModelAdmin):
    list_display = ['id', 'title', 'created_at']
    list_display_links = ['id', 'title']
    search_fields = ("title",)
    ordering = ("-created_at",)
    readonly_fields = ["created_at"]
    fieldsets = (
        (None, {"fields": ("title", "created_at")}),
    )

@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ['id', 'title', 'created_at']
    list_display_links = ['id', 'title']
    search_fields = ("title",)
    ordering = ("-created_at",)
    readonly_fields = ["created_at"]
    fieldsets = (
        (None, {"fields": ("title", "created_at")}),
    )

@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ['id', 'title', 'created_at']
    list_display_links = ['id', 'title']
    search_fields = ("title", "id") # Added ID search
    ordering = ("-created_at",)
    readonly_fields = ["created_at"]
    # Use autocomplete for ManyToManyFields for better UX
    autocomplete_fields = ['color', 'size', 'category', 'product_model']
    fieldsets = (
        (_("Основная информация"), {"fields": ("title", "created_at")}),
        (
            _("Характеристики"),
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

# --- Admin for Production models ---

@admin.register(ProductionBatch)
class ProductionBatchAdmin(ModelAdmin):
    list_display = ['batch_number', 'title', 'planned_completion_date', 'notes', 'is_completed', 'created_at']
    list_display_links = ['batch_number', 'title']
    search_fields = ('batch_number', 'title', 'notes') # Added search_fields
    list_filter = ('is_completed', 'planned_completion_date') # Useful filters
    readonly_fields = ["created_at"]
    fieldsets = (
        (
            _("Производственная Партия"),
            {
                "fields": (
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

    # def get_queryset(self, request):
    #     """
    #     Filter BatchProducts to show only those whose parent batch belongs
    #     to the user's filial, unless the user is a superuser.
    #     """
    #     qs = super().get_queryset(request)
    #     if request.user.is_superuser:
    #         return qs

    #     if hasattr(request.user, 'filial') and request.user.filial:
    #         return qs.filter(batch__filial=request.user.filial)
    #     else:
    #         return qs.none()
        
@admin.register(BatchProduct)
class BatchProductAdmin(ModelAdmin):
    list_display = ['batch', 'product', 'quantity_finish'] # Added quantity_finish
    list_display_links = ['batch', 'product']
    search_fields = ('batch__batch_number', 'batch__title', 'product__title') # Added search_fields
    list_filter = ('batch',) # Filter by batch
    # Use autocomplete for foreign keys
    autocomplete_fields = ['batch', 'product']
    fieldsets = (
        (
            _("Товар в Партии"),
            {
                "fields": (
                    "batch",
                    "product",
                    "quantity_finish", # Make sure this field is editable if needed
                )
            },
        ),
    )

    # def get_queryset(self, request):
    #     """
    #     Filter BatchProducts to show only those whose parent batch belongs
    #     to the user's filial, unless the user is a superuser.
    #     """
    #     qs = super().get_queryset(request)
    #     if request.user.is_superuser:
    #         return qs

    #     if hasattr(request.user, 'filial') and request.user.filial:
    #         return qs.filter(batch__filial=request.user.filial)
    #     else:
    #         return qs.none()
    
    
@admin.register(ProcessStage)
class ProcessStageAdmin(ModelAdmin):
    list_display = ['batch_product', 'stage_type', 'assigned_user', 'status',
                    'start_date', 'end_date', 'quantity_completed', 'quantity_defective',
                    'previous_stage', 'confirmed_by', 'confirmed_at']
    # Keep list_display_links concise for better readability
    list_display_links = ['batch_product', 'stage_type', 'assigned_user']
    readonly_fields = [
        "created_at",
        "updated_at",
        # Keep these readonly as they are likely set programmatically or by specific users
        # "confirmed_by",
        # "confirmed_at",
    ]
    # Define search fields needed for autocomplete (especially for 'previous_stage')
    # and general searching
    search_fields = [
        'id', # Search by ProcessStage ID (important for previous_stage autocomplete)
        'batch_product__batch__batch_number',
        'batch_product__product__title',
        'assigned_user__username',
        'status',
        'stage_type'
        ]
    # Corrected list_filter: removed invalid 'batch_product__batch__filial'
    list_filter = ('stage_type', 'status', 'assigned_user', 'batch_product__batch')
    fieldsets = (
        (
            _("Детали Этапа Процесса"),
            {
                "fields": (
                    'batch_product', 'stage_type',
                    'assigned_user', 'status',
                    ('start_date', 'end_date'),
                    ('quantity_completed', 'quantity_defective'),
                    'previous_stage',
                    # Consider if confirmed_by/at should be editable here
                    ('confirmed_by', 'confirmed_at'),
                    ('created_at', 'updated_at'),
                    'close_session',
                )
            },
        ),
    )
    # Enable autocomplete for ForeignKey/OneToOneFields
    autocomplete_fields = ['assigned_user', 'batch_product', 'previous_stage', 'confirmed_by']

    def get_queryset(self, request):
        print(f"--- User: {request.user}, Is Superuser: {request.user.is_superuser}, Is Staff: {request.user.is_staff}") # DEBUG
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            print("--- Returning full queryset for superuser") # DEBUG
            return qs
        if request.user.is_authenticated:
            print(f"--- Filtering for assigned user: {request.user}") # DEBUG
            filtered_qs = qs.filter(assigned_user=request.user)
            print(f"--- Filtered queryset count: {filtered_qs.count()}") # DEBUG
            return filtered_qs
        print("--- Returning empty queryset (user not authenticated?)") # DEBUG
        return qs.none()

   