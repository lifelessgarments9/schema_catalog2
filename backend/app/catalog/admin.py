import json
from django.contrib import admin
from django import forms
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

class DeviceAdminForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.spec_field_names = []

        category = self.instance.category if self.instance and self.instance.pk else None
        if not category: return

        current = self.instance.specifications or {}
        if isinstance(current, str):
            try:
                current = json.loads(current)
            except (TypeError, ValueError):
                current = {}

        for spec in Specification.objects.filter(category=category):
            field_name = f"spec__{spec.name}"
            self.fields[field_name] = forms.CharField(
                label=spec.name,
                required=False,
                initial=current.get(spec.name, ""),
            )
            self.spec_field_names.append(field_name)

        if "specifications" in self.fields:
            self.fields["specifications"].required = False

    def save(self, commit=True):
        if self.spec_field_names:
            self.instance.specifications = {
                name[len("spec__"):]: self.cleaned_data.get(name, "")
                for name in self.spec_field_names
                if self.cleaned_data.get(name, "")
            }
        return super().save(commit=commit)

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    form = DeviceAdminForm
    list_display = ['name', 'category', 'manufacturer', 'quantity', 'quantity_storage', 'quantity_rented', 'is_available']
    list_filter = ['category', 'is_available', 'manufacturer']
    search_fields = ['name', 'description', 'manufacturer']
    readonly_fields = ['embedding', 'quantity', 'quantity_rented']

    def get_form(self, request, obj=None, change=False, **kwargs):
        kwargs['fields'] = [
            'name', 'description', 'category',
            'specifications',
            'image', 'documentation', 'doc_text',
            'quantity', 'quantity_storage', 'quantity_rented', 'is_available', 'manufacturer',
            'embedding',
        ]
        return super().get_form(request, obj, change, **kwargs)

    def get_fieldsets(self, request, obj=None):
        spec_fields = []
        if obj and obj.category:
            spec_fields = [f"spec__{s.name}" for s in Specification.objects.filter(category=obj.category)]

        return (
            ('Основное', {'fields': ('name', 'description', 'category')}),
            ('Характеристики', {
                'fields': tuple(spec_fields) if spec_fields else ('specifications',),
            }),
            ('Файлы', {'fields': ('image', 'documentation', 'doc_text')}),
            ('Склад', {'fields': ('quantity', 'quantity_storage', 'quantity_rented', 'is_available', 'manufacturer')}),
            ('Эмбеддинг', {'fields': ('embedding',), 'classes': ('collapse',)}),
        )