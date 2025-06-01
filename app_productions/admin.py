#app_productions admin.py:
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.shortcuts import render

from django.db.models import Sum, Q # Import Q for complex lookups
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
    extra = 1 # Сколько пустых форм показывать для добавления
    fields = ('operation_type', 'rate')

@admin.register(Product)
class ProductAdmin(ModelAdmin): # или admin.ModelAdmin
    list_display = ['id', 'title', 'created_at']
    search_fields = ("title", "id")
    ordering = ("title",)
    readonly_fields = ["created_at"]
    autocomplete_fields = ['color', 'size', 'category', 'product_model']
    # filter_horizontal = ('color', 'size', 'category', 'product_model',)

    fieldsets = (
        (_("Основная информация"), {"fields": ("title", "created_at")}),
        (
            _("Характеристики"),
            {"fields": ("color", "size", "category", "product_model")}
        )
    )
    inlines = [ProductOperationRateInline] # Добавляем инлайн сюда
    actions = ['set_individual_rate_action']
    @admin.action(description='Установить индивидуальную ставку для выбранных товаров')
    def set_individual_rate_action(self, request, queryset):
        # Если пользователь нажал "Выполнить" на промежуточной странице
        if 'apply' in request.POST:
            form = SetIndividualRateForm(request.POST)
            if form.is_valid():
                operation_type = form.cleaned_data['operation_type']
                rate_value = form.cleaned_data['rate']
                # update_existing = form.cleaned_data.get('update_existing', False) # Если добавил чекбокс

                updated_count = 0
                created_count = 0
                for product in queryset:
                    # Логика создания или обновления ProductOperationRate
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

        # Если это первый шаг (выбор товаров и действия)
        else:
            form = SetIndividualRateForm()
        
        context = {
            **self.admin_site.each_context(request),
            'title': 'Установка индивидуальной ставки',
            'queryset': queryset,
            'form': form,
            'opts': self.model._meta, # Для корректного отображения хлебных крошек и т.д.
            'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME, # Для формы
        }
        # Используем кастомный шаблон для промежуточной страницы
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
class WorkLogAdmin(ModelAdmin): # или admin.ModelAdmin
    list_display = [
        'id',  
        'stage_link', # <<< Используем кастомный метод для ссылки на этап
        'user_display', # <<< Используем кастомный метод для пользователя
        'quantity_processed', 
        'quantity_defective',
        'log_time_display', # <<< Используем кастомный метод для времени
        'created_at_display' # <<< Используем кастомный метод для времени создания
    ]
    list_display_links = ['id', 'stage_link'] # Ссылки на редактирование
    search_fields = (
        'id', 
        'user__username', 
        'user__first_name', 
        'user__last_name', 
        'stage__id',  
        'stage__batch_product__product__title', # Поиск по названию товара
        'stage__batch_product__batch__batch_number', # Поиск по номеру партии
    )
    list_filter = ('user', 'stage__stage_type', 'log_time', 'created_at') # Добавь нужные фильтры
    date_hierarchy = 'log_time' # Удобная навигация по дате
    ordering = ['-log_time', '-id'] # Сначала новые
    list_select_related = ('stage__batch_product__product', 'stage__batch_product__batch', 'user') # Оптимизация

    # Для более красивого отображения связанных объектов
    @admin.display(description=_('Этап процесса'), ordering='stage__id')
    def stage_link(self, obj):
        if obj.stage:
            # Ссылка на сам ProcessStage
            stage_url = reverse('admin:app_productions_processstage_change', args=[obj.stage.pk])
            return format_html('<a href="{}">{}</a>', stage_url, str(obj.stage))
        return "-"

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