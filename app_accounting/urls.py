# В urls.py вашего приложения или в главном urls.py
from django.urls import path
from .views import UserProfileView, monthly_user_production_report,mark_salary_as_paid,  UserSalaryReportView


app_name = 'accounts'
urlpatterns = [
    path('profile/', UserSalaryReportView.as_view(), name='profile'),
    path('salary/<int:pk>/mark-paid/', mark_salary_as_paid, name='mark_salary_paid'),
    path('reports/monthly-user-production/', monthly_user_production_report, name='monthly_user_report'),
]



 





