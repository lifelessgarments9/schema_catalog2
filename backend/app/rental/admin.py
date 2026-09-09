from django.contrib import admin

from app.rental.models import Cart, CartItem, RentalRequest, RentalRequestItem

class DeviceFilter(admin.SimpleListFilter):
    title = "Устройство"
    parameter_name = "device"

    def lookups(self, request, model_admin):
        devices = (
            RentalRequestItem.objects
            .values_list("device__id", "device__name")
            .distinct()
            .order_by("device__name")
        )

        return devices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                items__device_id=self.value()
            ).distinct()

        return queryset

class RentalRequestItemInline(admin.TabularInline):
    model = RentalRequestItem
    extra = 0
    readonly_fields = ["device", "quantity", "return_date"]


@admin.register(RentalRequest)
class RentalRequestAdmin(admin.ModelAdmin):
    list_display  = ["id", "full_name", "group", "discipline", "status", "issue_date", "created_at"]
    list_filter   = ["status",DeviceFilter]
    search_fields = ["full_name", "group", "discipline", "student__username"]
    readonly_fields = ["student", "created_at"]
    inlines = [RentalRequestItemInline]


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ["user"]
    inlines = [CartItemInline]