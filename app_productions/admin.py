from django.contrib import admin
from django.db.models import Sum, Q # Import Q for complex lookups
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin # Use ModelAdmin from unfold consistently

# Import your models from the current app (.)
from .models import (
    ProductionBatch, ProcessStage, BatchProduct, Product,
    Color, Size, Product_Model, Category, WorkLog
)
# Import User model (adjust path if it's in a different app)
from app_users.models import User

# Assuming logger is configured (optional for admin actions)
import logging
logger = logging.getLogger(__name__)

# --- Admin for related basic models ---

@admin.register(Color)
class ColorAdmin(ModelAdmin):
    list_display = ['id', 'title', 'created_at']
    list_display_links = ['id', 'title']
    search_fields = ("title",)
    ordering = ("title",) # Consistent ordering
    readonly_fields = ["created_at"]
    fieldsets = (
        (None, {"fields": ("title", "created_at")}),
    )

@admin.register(Size)
class SizeAdmin(ModelAdmin):
    list_display = ['id', 'title', 'created_at']
    list_display_links = ['id', 'title']
    search_fields = ("title",)
    ordering = ("title",)
    readonly_fields = ["created_at"]
    fieldsets = (
        (None, {"fields": ("title", "created_at")}),
    )

@admin.register(Product_Model)
class ProductModelAdmin(ModelAdmin):
    list_display = ['id', 'title', 'created_at']
    list_display_links = ['id', 'title']
    search_fields = ("title",)
    ordering = ("title",)
    readonly_fields = ["created_at"]
    fieldsets = (
        (None, {"fields": ("title", "created_at")}),
    )

@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ['id', 'title', 'created_at']
    list_display_links = ['id', 'title']
    search_fields = ("title",)
    ordering = ("title",)
    readonly_fields = ["created_at"]
    fieldsets = (
        (None, {"fields": ("title", "created_at")}),
    )

@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ['id', 'title', 'created_at']
    list_display_links = ['id', 'title']
    search_fields = ("title", "id") # Added ID search
    ordering = ("title",)
    readonly_fields = ["created_at"]
    autocomplete_fields = ['color', 'size', 'category', 'product_model'] # Essential for M2M
    filter_horizontal = ('color', 'size', 'category', 'product_model',) # Alternative display for M2M if preferred over autocomplete
    fieldsets = (
        (_("Основная информация"), {"fields": ("title", "created_at")}),
        (
            _("Характеристики"),
            {
                # Use filter_horizontal OR autocomplete_fields, not usually both visually
                "fields": ( "color", "size", "category", "product_model",)
            }
        )
    )


@admin.register(ProductionBatch)
class ProductionBatchAdmin(ModelAdmin):
    list_display = ['batch_number', 'title', 'planned_completion_date', 'is_completed', 'created_at']
    list_display_links = ['batch_number', 'title']
    search_fields = ('batch_number', 'title', 'notes')
    list_filter = ('is_completed', 'planned_completion_date')
    readonly_fields = ["created_at"]
    date_hierarchy = 'created_at' # Useful for navigating by date
    fieldsets = (
        (
            _("Детали Партии"),
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
    # Add get_queryset filtering by filial here if needed in the future

@admin.register(BatchProduct)
class BatchProductAdmin(ModelAdmin):
    list_display = ['batch', 'product', 'quantity_finish']
    list_display_links = ['batch', 'product']
    search_fields = ('batch__batch_number', 'batch__title', 'product__title')
    list_filter = ('batch__is_completed', 'batch') # Filter by batch status and batch itself
    autocomplete_fields = ['batch', 'product'] # Essential for FKs
    list_select_related = ['batch', 'product'] # Optimize queries
    fieldsets = (
        (
            _("Товар в Партии"),
            {
                "fields": ( "batch", "product", "quantity_finish",)
            },
        ),
    )







@admin.register(ProcessStage)
class ProcessStageAdmin(ModelAdmin):
    list_display = [
        'batch_product', 'stage_type', 'status', 'assigned_user',
        'total_completed_display', # Use display methods for calculated totals
        'total_defective_display',
        'start_date', 'end_date',  #'confirmed_by', 'confirmed_at',
        'close_session'
    ]
    list_display_links = ['batch_product', 'stage_type'] # Keep concise
    list_filter = ('stage_type', 'status', 'assigned_user', 'batch_product__batch', 'close_session')
    search_fields = [
        'id', 'batch_product__batch__batch_number', 'batch_product__product__title',
        'assigned_user__username', 'status', 'stage_type'
    ]
    readonly_fields = [
        "created_at", "updated_at",
        'total_completed_display', 'total_defective_display', # Calculated fields are read-only
        #'confirmed_by', 'confirmed_at', # These might be set programmatically or by specific roles
    ]
    autocomplete_fields = ['assigned_user', 'batch_product', 'confirmed_by']
    list_select_related = [ # Optimize list view queries
        'batch_product__batch', 'batch_product__product', 'assigned_user',
         'confirmed_by'
        ]
    date_hierarchy = 'created_at'
    ordering = ['-created_at'] # Show newest stages first by default

    fieldsets = (
        (_("Связи и Статус"), {
            "fields": (
                'batch_product', 'stage_type', 'status','assigned_user','quantity_completed','quantity_deffect'
            )
        }),
        (_("Даты"), {
            "fields": (('start_date', 'end_date'),)
        }),
         
        (_("Подтверждение и Завершение"), {
             "fields": (
                 ('confirmed_by', 'confirmed_at'),
                 'close_session',
             ),
              "classes": ('collapse',),
        }),
         (_("Даты аудита"), {
             "fields": (('created_at', 'updated_at'),),
             "classes": ('collapse',),
         }),
    )

    actions = ['update_totals_from_logs_action'] # Add the admin action

    # --- Display Methods ---
    # @admin.display(description=_('Товар в партии'), ordering='batch_product__product__title')
    # def batch_product_link(self, obj):
    #     if obj.batch_product:
    #         link = reverse('admin:%s_%s_change' % (obj.batch_product._meta.app_label, obj.batch_product._meta.model_name), args=[obj.batch_product.pk])
    #         return format_html('<a href="{}">{}</a>', link, obj.batch_product)
    #     return "-"


    @admin.display(description=_('Выполнено Итого'), ordering='quantity_completed')
    def total_completed_display(self, obj):
        # Returns the stored value (updated by action/signal/etc.)
        return obj.quantity_completed

    @admin.display(description=_('Брак Итого'), ordering='quantity_defective')
    def total_defective_display(self, obj):
        # Returns the stored value
        return obj.quantity_deffect



    def get_queryset(self, request):
        """
        Переопределяем метод, чтобы ограничить видимость записей
        для не-суперпользователей.
        """
        # Получаем базовый queryset
        qs = super().get_queryset(request)

        # Если пользователь - суперпользователь, он видит все записи
        if request.user.is_superuser:
            return qs

        # Иначе, показываем только те записи, где assigned_user - это текущий пользователь
        # Убедитесь, что поле называется именно `assigned_user` в вашей модели ProcessStage
        return qs.filter(assigned_user=request.user)
        
    # --- Admin Action ---
    @admin.action(description=_('Обновить итоги этапа из записей о работе'))
    def update_totals_from_logs_action(self, request, queryset):
        updated_count = 0
        processed_count = 0
        for stage in queryset:
            processed_count +=1
            try:
                # Store old values to check if update happened
                old_completed = stage.quantity_completed
                old_defective = stage.quantity_deffect
                stage.update_stage_totals() # Call the model method
                # Refresh from DB to confirm the change for the check below
                stage.refresh_from_db(fields=['quantity_completed', 'quantity_deffect'])
                if stage.quantity_completed != old_completed or stage.quantity_deffect != old_defective:
                     updated_count += 1
            except Exception as e:
                logger.error(f"Error updating totals for stage {stage.id} via admin action: {e}", exc_info=True)
                self.message_user(request, f"Ошибка при обновлении этапа {stage.id}: {e}", level='error')

        if updated_count > 0:
            self.message_user(request, _(f'{updated_count} из {processed_count} этапов успешно обновлены.'), level='success')
        else:
             self.message_user(request, _(f'Итоги для {processed_count} этапов не изменились или уже были актуальны.'), level='warning')

@admin.register(WorkLog)
class WorkLogAdmin(ModelAdmin):
    list_display = ['stage', 'user__first_name', 'quantity_processed', 'quantity_defective']
    
    def get_queryset(self, request):
        """
        Переопределяем метод, чтобы ограничить видимость записей
        для не-суперпользователей.
        """
        # Получаем базовый queryset
        qs = super().get_queryset(request)

        # Если пользователь - суперпользователь, он видит все записи
        if request.user.is_superuser:
            return qs

        return qs.filter(user=request.user)