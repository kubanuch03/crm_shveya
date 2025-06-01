# app_accounting/admin.py
from django.contrib import admin
from unfold.admin import ModelAdmin # или from django.contrib import admin
from .models import UserSalary
from django.utils.translation import gettext_lazy as _

class PaymentStatusFilter(admin.SimpleListFilter):
    title = _('Статус выплаты') # Название фильтра
    parameter_name = 'is_paid'  # Используем имя поля модели для простоты

    def lookups(self, request, model_admin):
        """
        Возвращает варианты для фильтра: (значение_в_url, отображаемое_имя)
        """
        return (
            ('all', _('Все')), # Опция для отображения всех записей
            ('yes', _('Выплачено')),
            ('no', _('Не выплачено')),
        )

    def queryset(self, request, queryset):
        """
        Фильтрует queryset на основе выбранного значения.
        Если выбрано 'all' или ничего не выбрано (по умолчанию), показываем все.
        """
        if self.value() == 'yes':
            return queryset.filter(is_paid=True)
        if self.value() == 'no':
            return queryset.filter(is_paid=False)
        # Если self.value() == 'all' или None (по умолчанию), возвращаем queryset без изменений
        return queryset

@admin.register(UserSalary)
class UserSalaryAdmin(ModelAdmin):
    list_display = [
        'user_display',
        'salary_year', 
        'salary_month', 
        'total_cash_display',
        'is_paid', # Это поле будет показывать True/False
        'paid_at_display',
        'paid_by_display',
        'created_at_display'
    ]
    list_display_links = ['user_display']
    search_fields = ("user__username", "user__first_name", "user__last_name", "salary_year", "salary_month")
    list_filter = (
        PaymentStatusFilter, # <<< Наш обновленный фильтр
        'salary_year', 
        'salary_month', 
        'user__username' 
    )
    readonly_fields = ["created_at", "paid_at", "paid_by", "total_cash_display"]
    ordering = ['-salary_year', '-salary_month', 'is_paid', 'user__username']

    @admin.display(description=_('Сотрудник'), ordering='user__username')
    def user_display(self, obj):
        return obj.user.get_full_name() or obj.user.username

    @admin.display(description=_('Заработано (сом)'), ordering='total_cash')
    def total_cash_display(self, obj):
        return f"{obj.total_cash:.2f}" if obj.total_cash is not None else "0.00"

    @admin.display(description=_('Дата выплаты/закрытия'), ordering='paid_at')
    def paid_at_display(self, obj):
        return obj.paid_at.strftime('%d.%m.%Y %H:%M') if obj.paid_at else '-'
    
    @admin.display(description=_('Кем закрыто'), ordering='paid_by__username')
    def paid_by_display(self, obj):
        if obj.paid_by:
            return obj.paid_by.get_full_name() or obj.paid_by.username
        return "-"
    
    @admin.display(description=_('Дата Создания записи'), ordering='created_at')
    def created_at_display(self, obj):
        return obj.created_at.strftime('%d.%m.%Y %H:%M') if obj.created_at else '-'

    def get_queryset(self, request):
        qs =  super().get_queryset(request)
        # Фильтрация для не-суперпользователей, если это нужно
        # if not request.user.is_superuser:
        #      qs = qs.filter(user=request.user)
        return qs.select_related('user', 'paid_by') # Оптимизация