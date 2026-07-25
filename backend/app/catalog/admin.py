from django.contrib import admin
from .models import Category, Device


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'specification_template']
    search_fields = ['name']


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'manufacturer', 'quantity', 'is_available']
    list_filter = ['category', 'is_available', 'manufacturer']
    search_fields = ['name', 'description', 'manufacturer']
    fieldsets = (
        ('Основное', {
            'fields': ('name', 'description', 'category')
        }),
        ('Характеристики', {
            'fields': ('specifications',)
        }),
        ('Файлы', {
            'fields': ('image', 'documentation', 'doc_text')
        }),
        ('Склад', {
            'fields': ('quantity', 'is_available', 'manufacturer')
        }),
        ('Эмбеддинг', {
            'fields': ('embedding',),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ['embedding']