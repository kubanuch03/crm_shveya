from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import PackagingSettings, UtugSettings, TailorSettings
from unfold.admin import ModelAdmin # Use ModelAdmin from unfold consistently



@admin.register(UtugSettings)
class UtugSettingsAdmin(ModelAdmin):
    list_display = [
        'title', 'per_unit', 'created_at',
    ]
    list_display_links = ['title', 'per_unit', 'created_at']
    list_filter = ('title',)
    search_fields = [
        'title'
    ]
    readonly_fields = [
        "created_at", 
    ]
    # autocomplete_fields = ['assigned_user', 'batch_product', 'confirmed_by']
    # list_select_related = [ 
    #     'title',
    #     ]
    date_hierarchy = 'created_at'
    ordering = ['-created_at'] 

    fieldsets = (
        (_("Информация"), {
            "fields": (
                'title', 'per_unit',
            )
        }),
        (_("Даты"), {
            "fields": (('created_at'),)
        }),
    )




@admin.register(PackagingSettings)
class PackagingSettingsAdmin(ModelAdmin):
    list_display = [
        'title', 'per_unit', 'created_at',
    ]
    list_display_links = ['title', 'per_unit', 'created_at']
    list_filter = ('title',)
    search_fields = [
        'title'
    ]
    readonly_fields = [
        "created_at", 
    ]
    # autocomplete_fields = ['assigned_user', 'batch_product', 'confirmed_by']
    # list_select_related = [ 
    #     'title',
    #     ]
    date_hierarchy = 'created_at'
    ordering = ['-created_at'] 

    fieldsets = (
        (_("Информация"), {
            "fields": (
                'title', 'per_unit',
            )
        }),
        (_("Даты"), {
            "fields": (('created_at'),)
        }),
    )



@admin.register(TailorSettings)
class TailorSettingsAdmin(ModelAdmin):
    list_display = [
        'title', 'per_unit', 'created_at',
    ]
    list_display_links = ['title', 'per_unit', 'created_at']
    list_filter = ('title',)
    search_fields = [
        'title'
    ]
    
    readonly_fields = [
        "created_at", 
    ]
    # autocomplete_fields = ['assigned_user', 'batch_product', 'confirmed_by']
    # list_select_related = [ 
    #     'title',
    #     ]
    date_hierarchy = 'created_at'
    ordering = ['-created_at'] 

    fieldsets = (
        (_("Информация"), {
            "fields": (
                'title', 'per_unit',
            )
        }),
        (_("Даты"), {
            "fields": (('created_at'),)
        }),
    )

