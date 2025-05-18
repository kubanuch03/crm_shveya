from django.contrib import admin
from unfold.admin import ModelAdmin # Use ModelAdmin from unfold consistently
from .models import UserSalary


@admin.register(UserSalary)
class UserSalaryAdmin(ModelAdmin):
    list_display = ['user', 'total_cash', 'created_at']
    list_display_links = ['user', 'total_cash', 'created_at']
    search_fields = ("user__first_name","user__username", "user__last_name")
    readonly_fields = ["created_at"]
    


    def get_queryset(self, request):
        qs =  super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)
