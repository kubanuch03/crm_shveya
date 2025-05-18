from django.db import models
from datetime import datetime
from django.core.exceptions import ValidationError
from django.utils import timezone
from app_productions.models import WorkLog
from app_users.models import User



class IsGetSalary(models.Model):
    title = models.CharField(max_length=255, verbose_name='Наименование')
    cash = models.PositiveIntegerField(default=0, blank=True, null=True, verbose_name='Сом')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создание')

class UserSalary(models.Model):
    work_log = models.ManyToManyField(
        WorkLog,
        blank=True,
        verbose_name='Записи о работе'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Сотрудник')
    salary_period_date = models.DateField(
        null=True,
        verbose_name='Месяц и год зарплаты',
        help_text='Любая дата в месяце, за который начисляется зарплата. Будет использован только месяц и год.'
    )
    salary_year = models.PositiveIntegerField(null=True, verbose_name='Год зарплаты')
    salary_month = models.PositiveIntegerField(null=True, verbose_name='Месяц зарплаты')
    total_cash = models.PositiveIntegerField(default=0, verbose_name='Заработано') 
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата Создания записи')

    def __str__(self):
        return f"Зарплата {self.user.first_name or self.user.username} за {self.salary_month:02d}/{self.salary_year}"

    class Meta:
        verbose_name = 'Заработная плата Сотрудников'
        verbose_name_plural = 'Заработная плата Сотрудников'
        ordering = ['-salary_year', '-salary_month', 'user__username']

    

   
    