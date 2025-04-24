from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from django.contrib.auth import get_user_model
# from .models import Profile
from .forms import UserProfileForm # Вам нужно будет создать эту форму

User = get_user_model()
def dashboard_callback(request, context):
    """
    Обновляет переданный контекст, добавляя виджеты и данные для шаблона,
    и возвращает ИЗМЕНЕННЫЙ контекст.
    """
    # 1. Создаем список описаний виджетов
    widgets = [
        # --- Виджет профиля ---
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
        # --- Сюда можно добавить другие виджеты ---
        # ...
    ]

    # 2. Добавляем наши виджеты и ДАННЫЕ ДЛЯ ШАБЛОНА в контекст
    context.update({
        # Ключ, который Unfold использует для отображения виджетов (проверьте документацию, может быть другим)
        "dashboard_widgets": widgets,
        # Добавляем данные, которые нужны вашему шаблону index.html
        "total_users": User.objects.count(),
        "latest_user": User.objects.order_by('-date_joined').first(),
        # Можно добавить и другие переменные
    })

    # 3. Возвращаем ОБНОВЛЕННЫЙ СЛОВАРЬ контекста
    return context

# --- Ваш UserProfileView ---
class UserProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'admin/profile/profile_form.html' # Укажите путь к шаблону формы
    success_url = reverse_lazy('accounts:profile') # Куда перенаправить после сохранения

    def get_object(self, queryset=None):
        return self.request.user # Редактируем текущего пользователя

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(admin.site.each_context(self.request))
        context['title'] = 'Мой профиль'
        return context