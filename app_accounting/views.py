from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.views.generic import DetailView
# from .models import Profile
from .forms import UserProfileForm # Вам нужно будет создать эту форму
from rest_framework.views import APIView
from rest_framework.response import Response
from app_productions.serializers import ProductionBatchSerializer
from logger import logger

import datetime
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required 
from django.utils import timezone
from django.db.models import Sum, F, Value, CharField
from django.db.models.functions import Concat
from app_users.models import User 
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from datetime import date
from app_accounting.models import UserSalary 
from app_productions.models import ProcessStage, WorkLog
from django.shortcuts import get_object_or_404, Http404 


def dashboard_callback(request, context):
    """
    Обновляет переданный контекст, добавляя виджеты и данные для шаблона,
    и возвращает ИЗМЕНЕННЫЙ контекст.
    """
    widgets = [
        {
            "title": _("Мой профиль"),
            "icon": "account_circle",
            "actions": [
                {
                    "title": _("Редактировать профиль"),
                    "link": reverse_lazy("accounts:profile"),
                    "icon": "edit",
                }
            ],
            "description": _("Просмотр и редактирование личных данных."),
            "permission": lambda req: req.user.is_authenticated,
        },
    ]

    context.update({
        "dashboard_widgets": widgets,
        "total_users": User.objects.count(),
        "latest_user": User.objects.order_by('-date_joined').first(),
    })

    return context

# --- Ваш UserProfileView ---
class UserProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'admin/profile/profile_form.html' 
    success_url = reverse_lazy('accounts:profile')

    def get_object(self, queryset=None):
        return self.request.user 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(admin.site.each_context(self.request))
        context['title'] = 'Мой профиль'
        return context

# --- Ваш UserProfileView ---
class UserProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'admin/profile/profile_form.html' 
    success_url = reverse_lazy('accounts:profile')

    def get_object(self, queryset=None):
        return self.request.user 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(admin.site.each_context(self.request))
        context['title'] = 'Мой профиль'
        return context

class UserSalaryReportView(LoginRequiredMixin, DetailView):
    model = UserSalary
    template_name = "admin/profile/profile_form.html" # Убедитесь, что путь к шаблону правильный
    context_object_name = "usersalary" # Это имя будет использоваться в шаблоне для доступа к объекту UserSalary

    def get_object(self, queryset=None):
        user = self.request.user
        today = date.today()
        try:
            # Пытаемся получить зарплату за текущий месяц
            return UserSalary.objects.get(
                user=user,
                salary_year=today.year,
                salary_month=today.month
            )
        except UserSalary.DoesNotExist:
            # Если за текущий месяц нет, попробуем найти последнюю доступную
            return UserSalary.objects.filter(user=user).order_by('-salary_year', '-salary_month').first()
        # Если и последней нет, .first() вернет None, и self.object (usersalary в шаблоне) будет None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) # Получаем базовый контекст от DetailView
                                                    # Он уже будет содержать 'usersalary': self.object

        # self.object это наш экземпляр UserSalary (или None, если не найден)
        # В шаблоне он будет доступен как {{ usersalary }}
        current_usersalary_object = self.object 

        if current_usersalary_object:
            context['no_salary_data_found'] = False
            context['title'] = _("Отчет по зарплате: %(user_name)s (%(month)02d/%(year)d)") % {
                'user_name': current_usersalary_object.user.get_full_name() or current_usersalary_object.user.username,
                'month': current_usersalary_object.salary_month,
                'year': current_usersalary_object.salary_year
            }

            # Получаем связанные WorkLog для ЭТОЙ конкретной UserSalary
            # Но если вы хотите передать их под другим именем или предварительно обработать:
            context['related_work_logs'] = current_usersalary_object.work_log.select_related('stage', 'stage__batch_product', 'stage__batch_product__batch', 'stage__batch_product__product').all()
            # select_related для оптимизации запросов в шаблоне

            # Расчет общего количества обработанных единиц (если нужно отдельно)
            total_items_aggregation = current_usersalary_object.work_log.aggregate(
                total_processed=Sum('quantity_processed')
            )
            context['total_items_processed'] = total_items_aggregation['total_processed'] or 0
            
            # Определение роли (ваша логика)
            user_role = _("Не определена")
            # ... (ваша логика определения user_role, используя current_usersalary_object.user ...)
            context['user_role'] = user_role

        else:
            context['no_salary_data_found'] = True
            context['title'] = _("Данные о зарплате не найдены")
            context['current_profile_user'] = self.request.user 

        return context
    
    

def monthly_user_production_report(request):
    """
    Отображает отчет о выполненной работе пользователей по типам этапов
    за текущий месяц и предоставляет возможность скачивания в XLSX.
    """
    now = timezone.now()
    current_year = now.year
    current_month = now.month

    first_day_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    if current_month == 12:
        first_day_of_next_month = first_day_of_month.replace(year=current_year + 1, month=1)
    else:
        first_day_of_next_month = first_day_of_month.replace(month=current_month + 1)

    # --- Фильтрация данных ---
    # Фильтруем этапы, завершенные (имеющие end_date) в текущем месяце
    # и имеющие статус 'COMPLETED'.
    # Также убеждаемся, что пользователь назначен.
    report_queryset = ProcessStage.objects.filter(
        end_date__gte=first_day_of_month,
        end_date__lt=first_day_of_next_month, # Используем "меньше", чем начало следующего месяца
        status='COMPLETED', # Или 'CONFIRMED', если это более подходящий статус
        assigned_user__isnull=False
    ).select_related('assigned_user') # Оптимизация запроса к пользователю

    report_data = report_queryset.values(
        'assigned_user', # Группируем по ID пользователя
        'stage_type'     # Группируем по типу этапа
    ).annotate(
        # Получаем ФИО пользователя для отображения
        user_full_name=Concat(
            F('assigned_user__last_name'), Value(' '), F('assigned_user__first_name'),
            output_field=CharField()
        ),
        username=F('assigned_user__username'), # Или используй username, если ФИО не всегда есть
        total_completed=Sum('quantity_completed') # Суммируем выполненное количество
    ).order_by(
        'user_full_name', # Сортируем по ФИО
        'stage_type'      # Затем по типу этапа
    ).values( # Выбираем только нужные поля для вывода
        'user_full_name',
        'username',
        'stage_type',
        'total_completed'
    )

    # --- Обработка запроса на экспорт в XLSX ---
    if request.GET.get('export') == 'xlsx':
        # Создаем Excel книгу
        wb = Workbook()
        ws = wb.active
        ws.title = _("Месячный отчет") # Используем перевод

        # Названия месяцев для заголовка файла и листа
        month_names = {
            1: _("Январь"), 2: _("Февраль"), 3: _("Март"), 4: _("Апрель"),
            5: _("Май"), 6: _("Июнь"), 7: _("Июль"), 8: _("Август"),
            9: _("Сентябрь"), 10: _("Октябрь"), 11: _("Ноябрь"), 12: _("Декабрь"),
        }
        current_month_name = month_names.get(current_month, "")

        ws.append([_("Отчет по производству за {} {}").format(current_month_name, current_year)])
        ws.append([]) # Пустая строка для отступа

        # Заголовки таблицы
        headers = [_('Пользователь (ФИО)'), _('Псевдоним'), _('Тип Этапа'), _('Выполнено (шт.)')]
        ws.append(headers)

        # Получаем словарь соответствия кодов этапов их отображаемым именам
        stage_display_names = dict(ProcessStage.STAGE_CHOICES)

        # Заполняем данными
        for item in report_data:
            # Получаем читаемое название этапа
            stage_name = stage_display_names.get(item['stage_type'], item['stage_type']) # Отображаемое имя или код, если не найдено
            ws.append([
                item['user_full_name'],
                item['username'],
                stage_name,
                item['total_completed']
            ])

        # Автоматическая ширина колонок (простая версия)
        for col_idx, header in enumerate(headers, 1):
             column_letter = get_column_letter(col_idx)
             ws.column_dimensions[column_letter].width = 20 # Можешь настроить ширину

        # Создаем HTTP ответ с файлом
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        filename = f"production_report_{current_year}_{current_month:02d}.xlsx"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        wb.save(response)
        return response

    # --- Отображение HTML страницы ---
    context = {
        'report_data': list(report_data), # Преобразуем в список для шаблона
        'current_month': current_month,
        'current_year': current_year,
        'stage_choices_dict': dict(ProcessStage.STAGE_CHOICES), # Передаем словарь для отображения названий в шаблоне
        'page_title': _("Отчет по производству за текущий месяц") # Для <title> и заголовка
    }
    return render(request, 'reports/monthly_user_production_report.html', context)


# class ProductionBatchAPIView(APIView):
#     def post(self, request):
#         serializer = ProductionBatchSerializer(data=request.data)
#         if not serializer.is_valid():
#             logger.error(f"Error serializers: {serializer.error}")
#             return Response(serializer.error, status=400)


