from django.contrib import admin

from unfold.admin import ModelAdmin

from .models import User

class UserAdmin(ModelAdmin):
    list_display = ['id','username','email','is_superuser']
    list_display_links = ['id','username','email']


admin.site.register(User, UserAdmin)