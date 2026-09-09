from django.contrib import admin
from .models import Category, Device, Specification

class SpecificationInline(admin.TabularInline):
    model = Specification
    extra = 1
    fields = ["name"]

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    inlines = [SpecificationInline]

@admin.register(Specification)
class SpecificationAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']
    list_filter = ['category']
    search_fields = ['name', 'category__name']

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'manufacturer', 'quantity','quantity_storage','quantity_rented', 'is_available']
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
            'fields': ('quantity','quantity_storage','quantity_rented', 'is_available', 'manufacturer')
        }),
        ('Эмбеддинг', {
            'fields': ('embedding',),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ['embedding','quantity','quantity_rented',]
