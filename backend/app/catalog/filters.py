from django.db.models import QuerySet


class DeviceFilter:

    def __init__(self, queryset: QuerySet, params: dict):
        self.queryset = queryset
        self.params = params

    def apply(self) -> QuerySet:
        qs = self.queryset

        category = self.params.get("category")
        if category: qs = qs.filter(category_id=int(category))

        manufacturer = self.params.get("manufacturer")
        if manufacturer: qs = qs.filter(manufacturer__icontains=manufacturer)

        if "is_available" in self.params:
            flag = self.params["is_available"].lower() == "true"
            qs = qs.filter(is_available=flag)

        min_qty=self.params.get("min_quantity")
        if min_qty: qs = qs.filter(quantity__gte=int(min_qty))

        search = self.params.get("search")
        if search: qs = qs.filter(name__icontains=search) | qs.filter(description__icontains=search)

        return qs
