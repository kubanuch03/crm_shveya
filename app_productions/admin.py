#app_productions admin.py:
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.shortcuts import render

from django.db.models import Sum, Q 
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin, TabularInline
from django import forms
from .models import (
    ProductionBatch, ProcessStage, BatchProduct, Product,ProductOperationRate,
    Color, Size, Product_Model, Category, WorkLog, OPERATION_TYPE_CHOICES
)
from app_users.models import User

import logging
logger = logging.getLogger(__name__)




class SetIndividualRateForm(forms.Form):
    operation_type = forms.ChoiceField(choices=OPERATION_TYPE_CHOICES, label="Тип операции")
    rate = forms.DecimalField(max_digits=10, decimal_places=2, label="Индивидуальная ставка")


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



class ProductOperationRateInline(TabularInline): # или StackedInline
    model = ProductOperationRate
    extra = 1 
    fields = ('operation_type', 'rate')

@admin.register(Product)
class ProductAdmin(ModelAdmin): # или admin.ModelAdmin
    list_display = ['id', 'title', 'created_at']
    list_display_links = ['id', 'title','created_at']
    search_fields = ("title", "id")
    ordering = ("title",)
    readonly_fields = ["created_at",]
    autocomplete_fields = ['color', 'size', 'category', 'product_model']
 
    fieldsets = (
        (_("Основная информация"), {"fields": ("title", "created_at")}),
        (
            _("Характеристики"),
            {"fields": ("quentity", "color", "size", "category", "product_model")}
        )
    )
    inlines = [ProductOperationRateInline] 
    actions = ['set_individual_rate_action']
    @admin.action(description='Установить индивидуальную ставку для выбранных товаров')
    def set_individual_rate_action(self, request, queryset):
        if 'apply' in request.POST:
            form = SetIndividualRateForm(request.POST)
            if form.is_valid():
                operation_type = form.cleaned_data['operation_type']
                rate_value = form.cleaned_data['rate']

                updated_count = 0
                created_count = 0
                for product in queryset:
                    obj, created = ProductOperationRate.objects.update_or_create(
                        product=product,
                        operation_type=operation_type,
                        defaults={'rate': rate_value}
                    )
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
                
                if created_count > 0:
                    self.message_user(request, f"{created_count} новых индивидуальных ставок успешно создано.", messages.SUCCESS)
                if updated_count > 0:
                    self.message_user(request, f"{updated_count} существующих индивидуальных ставок успешно обновлено.", messages.SUCCESS)
                if created_count == 0 and updated_count == 0:
                    self.message_user(request, "Не было создано или обновлено ни одной ставки (возможно, они уже существовали с таким же значением).", messages.WARNING)
                
                return HttpResponseRedirect(request.get_full_path()) # Обновить страницу

        else:
            form = SetIndividualRateForm()
        
        context = {
            **self.admin_site.each_context(request),
            'title': 'Установка индивидуальной ставки',
            'queryset': queryset,
            'form': form,
            'opts': self.model._meta, 
            'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME, # Для формы
        }
        return render(request, 'admin/actions/set_individual_rate_intermediate.html', context)

@admin.register(ProductOperationRate)
class ProductOperationRateAdmin(ModelAdmin): # или admin.ModelAdmin
    list_display = ('product', 'operation_type', 'rate', 'updated_at')
    list_filter = ('operation_type', 'product')
    search_fields = ('product__title', 'operation_type')
    autocomplete_fields = ['product']

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
    list_display = ['batch', 'quantity_finish']
    list_display_links = ['batch',]
    search_fields = ('batch__batch_number', 'batch__title', 'product__title')
    list_filter = ('batch__is_completed', 'batch') # Filter by batch status and batch itself
    autocomplete_fields = ['batch', 'product'] # Essential for FKs
    list_select_related = ['batch',] # Optimize queries
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
        'stage_type', 'status', 'assigned_user',
        'total_completed_display', # Use display methods for calculated totals
        'total_defective_display',
        'start_date', 'end_date',  #'confirmed_by', 'confirmed_at',
        'close_session'
    ]
    list_display_links = ['stage_type'] 
    list_filter = ('stage_type', 'status', 'assigned_user', 'batch_product__batch', 'close_session')
    search_fields = [
        'id', 'batch_product__batch__batch_number', 'batch_product__product__title',
        'assigned_user__username', 'status', 'stage_type'
    ]
    readonly_fields = [
        "created_at", "updated_at",
        'total_completed_display', 'total_defective_display',
        "assigned_user", 'stage_type'
    ]
    autocomplete_fields = ['batch_product', 'confirmed_by']
    list_select_related = [ 
         'assigned_user',
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
    
    
    
     

    def save_model(self, request, obj, form, change):
        """
        Принудительно устанавливает 'assigned_user' и 'stage_type'
        при создании нового объекта.
        """
        if not change:
            obj.assigned_user = request.user
            
            if request.user.status_staff == 'is_upakovka':
                obj.stage_type = 'PACKING'
            elif request.user.status_staff == 'is_tailor':
                obj.stage_type = 'SEWING'
        super().save_model(request, obj, form, change)

    @admin.display(description=_('Выполнено Итого'), ordering='quantity_completed')
    def total_completed_display(self, obj):
        # Returns the stored value (updated by action/signal/etc.)
        return obj.quantity_completed

    @admin.display(description=_('Брак Итого'), ordering='quantity_defective')
    def total_defective_display(self, obj):
        return obj.quantity_deffect



    def get_queryset(self, request):
        """
        Переопределяем метод, чтобы ограничить видимость записей
        для не-суперпользователей.
        """
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs

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
    list_display = [
        'id',  
        'stage',
        'user_display',
        'quantity_processed', 
        'quantity_defective',
        'log_time_display',
        'created_at_display' 
    ]
    list_display_links = ['id', 'stage'] 
    search_fields = (
        'id', 
        'user__username', 
        'user__first_name', 
        'user__last_name', 
        'stage__id',  
        'stage__batch_product__product__title', 
        'stage__batch_product__batch__batch_number',
    )
    list_filter = ('user', 'stage__stage_type', 'log_time', 'created_at', ) # Добавь нужные фильтры
    date_hierarchy = 'log_time' # Удобная навигация по дате
    ordering = ['-log_time', '-id'] # Сначала новые
    list_select_related = ['user', 'stage', ] # Оптимизация
 

    @admin.display(description=_('Сотрудник'), ordering='user__username')
    def user_display(self, obj):
        return obj.user.get_full_name() or obj.user.username

    @admin.display(description=_('Время записи лога'), ordering='log_time')
    def log_time_display(self, obj):
        return obj.log_time.strftime('%d.%m.%Y %H:%M') if obj.log_time else '-'
        
    @admin.display(description=_('Дата создания записи'), ordering='created_at')
    def created_at_display(self, obj):
        return obj.created_at.strftime('%d.%m.%Y %H:%M') if obj.created_at else '-'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs.select_related(*self.list_select_related) # Применяем select_related и здесь
        return qs.filter(user=request.user).select_related(*self.list_select_related)