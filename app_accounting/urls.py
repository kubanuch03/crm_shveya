# В urls.py вашего приложения или в главном urls.py
from django.urls import path
from .views import UserProfileView, monthly_user_production_report


app_name = 'accounts'
urlpatterns = [
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('reports/monthly-user-production/', monthly_user_production_report, name='monthly_user_report'),
]