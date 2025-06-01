# /app/app_accounting/forms.py

from django import forms
from django.contrib.auth import get_user_model
# Если у вас есть отдельная модель профиля, импортируйте ее:
# from .models import Profile

User = get_user_model() # Получаем стандартную модель пользователя Django

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email'] 