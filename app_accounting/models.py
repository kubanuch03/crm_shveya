# app_accounting/models.py
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from decimal import Decimal 

from app_productions.models import WorkLog 
from app_users.models import User 

import logging
logger = logging.getLogger(__name__)

class IsGetSalary(models.Model): 
    title = models.CharField(max_length=255, verbose_name='Наименование')
    cash = models.PositiveIntegerField(default=0, blank=True, null=True, verbose_name='Сом')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создание')

    def __str__(self):
        return self.title


class UserSalary(models.Model):
    work_log = models.ManyToManyField(WorkLog, blank=True, verbose_name=_('Записи о работе'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('Сотрудник'))
    
    salary_year = models.PositiveIntegerField(verbose_name=_('Год'))
    salary_month = models.PositiveIntegerField(verbose_name=_('Месяц'))
    salary_period_date = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    period_start_datetime = models.DateTimeField(default=timezone.now, verbose_name=_("Начало текущего расчетного периода"))
    total_cash = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name=_('Заработано за этот период'))
    
    is_paid = models.BooleanField(default=False, verbose_name=_("Этот период выплачен"))
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Дата выплаты этого периода"))
    paid_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='closed_salary_periods', verbose_name=_("Кто выплатил этот период"))
    
    created_at = models.DateTimeField(auto_now_add=True) 

    class Meta:
        verbose_name = 'Расчетный период зарплаты сотрудника'
        verbose_name_plural = 'Расчетные периоды зарплаты сотрудников'
        ordering = ['is_paid', '-salary_year', '-salary_month', '-period_start_datetime']

    def __str__(self):
        status = "Выплачено" if self.is_paid else "Активен"
        return f"ЗП {self.user.username} за период с {self.period_start_datetime.strftime('%d.%m.%Y %H:%M')} ({status})"

    def mark_as_paid_and_prepare_next(self, user_who_marked):
        if not self.is_paid:
            self.is_paid = True
            self.paid_at = timezone.now()
            self.paid_by = user_who_marked
            self.save(update_fields=['is_paid', 'paid_at', 'paid_by'])
            logger.info(f"UserSalary ID {self.pk} (период с {self.period_start_datetime}) для {self.user.username} помечен как выплаченный.")
            
            # !!! ЛОГИКА СОЗДАНИЯ НОВОГО ПЕРИОДА СРАЗУ ПОСЛЕ ВЫПЛАТЫ !!!
            # Создаем новую, "чистую" UserSalary для этого же пользователя и этого же месяца,
            # но с новой period_start_datetime (текущее время)
            new_period_salary = UserSalary.objects.create(
                user=self.user,
                salary_year=self.salary_year,
                salary_month=self.salary_month,
                period_start_datetime=timezone.now(), # Новый период начинается сейчас
                total_cash=Decimal('0.00'),
                is_paid=False
            )
            logger.info(f"Создан новый активный UserSalary ID {new_period_salary.pk} для {self.user.username} за {self.salary_month}/{self.salary_year} (период с {new_period_salary.period_start_datetime}).")
            return True, new_period_salary # Возвращаем признак успеха и новый объект
        return False, None