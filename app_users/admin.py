from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.models import Group
from unfold.admin import ModelAdmin
from .models import User
from .forms import CustomUserCreationForm, CustomUserChangeForm

from django.contrib.admin.options import IS_POPUP_VAR
from django.shortcuts import render

class UserAdmin(ModelAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm

    list_display = ['id', 'display_image', 'first_name', 'last_name', 'username', 'email', 'is_active', 'is_superuser',]
    list_display_links = ['id', 'display_image', 'username', 'email']
    readonly_fields = ['id', 'created_at']
    list_filter = ['is_active']
    search_fields = ('username', 'email')
    ordering = ('username',)
    filter_horizontal = ('groups',)
    add_fieldsets = (
        ('Authentication', {
            'fields': ('username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'is_active', 'is_staff'),
        }),
    )

    fieldsets = [
        (
            'User',
            {
                "fields": ("id", "image", 'first_name', 'last_name', "username", 'created_at', "email", "password"),
            },
        ),
        (
            "Permissions",
            {
                "classes": ["unfold-collapse"],
                "fields": [
                    "is_superuser", "is_staff", "is_active", "is_technolog", "is_upakovka", "is_utug", "is_croi",
                    "is_buttons", "is_tailor", "is_povar","groups",
                ],
            },
        ),
    ]

    def add_view(self, request, form_url='', extra_context=None):
        """Кастомизация страницы добавления с поддержкой Unfold."""
        extra_context = extra_context or {}
        extra_context['unfold_classes'] = 'unfold unfold-collapse'  # Ваши классы
        return super().add_view(request, form_url, extra_context=extra_context)
    
    def get_form(self, request, obj=None, **kwargs):
        """Используем CustomUserCreationForm при добавлении пользователя."""
        if obj is None:  
            kwargs['form'] = self.add_form
        return super().get_form(request, obj, **kwargs)

    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="60" height="50" />', obj.image.url)
        return "No Image"

    display_image.short_description = "Фото"



class CustomGroupAdmin(ModelAdmin):
    list_display = ('name',)  
    search_fields = ('name',)  
    ordering = ('name',) 

    fieldsets = [
        (None, {
            'fields': ('name', 'permissions'),  
        }),
    ]

admin.site.unregister(Group) 
admin.site.register(Group, CustomGroupAdmin)
admin.site.register(User, UserAdmin)