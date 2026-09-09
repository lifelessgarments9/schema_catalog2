from datetime import date
from django.db import transaction

from app.catalog.models import Device
from app.rental.models import Cart, CartItem, RentalRequest, RentalRequestItem

class RentalRequestService:

    @staticmethod
    def get_requests(user):
        qs = RentalRequest.objects.prefetch_related("items", "items__device").exclude(status="hidden").order_by("-created_at")
        return qs.all() if user.is_staff else qs.filter(student=user)

    @staticmethod
    @transaction.atomic
    def create(student, data):
        items_data = data.pop("items")

        rental = RentalRequest.objects.create(
            student=student,
            **data
        )

        RentalRequestItem.objects.bulk_create([
            RentalRequestItem(
                request=rental,
                device=item["device"],
                quantity=item["quantity"],
                return_date=item["return_date"],
            )
            for item in items_data
        ])

        CartService.clear(student.id)

        return rental

    @staticmethod
    @transaction.atomic
    def approve(request_id):
        rental = (RentalRequest.objects.prefetch_related("items", "items__device").get(pk=request_id))
        if rental.status != "pending":raise ValueError("Заявка уже обработана.")

        items = list(rental.items.all())
        device_ids = [item.device_id for item in items]

        devices = {
            device.id: device
            for device in Device.objects
            .select_for_update()
            .filter(id__in=device_ids)
            .order_by("id")
        }
        #проверка
        for item in items:
            device = devices[item.device_id]
            if device.quantity_storage < item.quantity:
                raise ValueError(
                    f"Недостаточно «{device.name}» на складе. "
                    f"Доступно: {device.quantity_storage}, "
                    f"требуется: {item.quantity}."
                )

        # всё хватает — списываем
        for item in items:
            device = devices[item.device_id]
            device.quantity_storage -= item.quantity
            device.quantity_rented += item.quantity
            device.is_available = device.quantity_storage > 0

        Device.objects.bulk_update(devices.values(), ["quantity_storage", "quantity_rented", "is_available"])
        rental.status = "approved"
        rental.issue_date = date.today()

        rental.save(update_fields=["status", "issue_date"])
        return rental

    @staticmethod
    @transaction.atomic
    def delete(request_id):
        rental = RentalRequest.objects.get(pk=request_id)

        if rental.status != "pending":
            raise ValueError("Можно скрыть только заявку, ожидающую подтверждения.")

        rental.status = "hidden"
        rental.save(update_fields=["status"])

    @staticmethod
    @transaction.atomic
    def return_devices(request_id):
        rental = RentalRequest.objects.prefetch_related("items","items__device").get(pk=request_id)
        if rental.status != "approved": raise ValueError("Вернуть можно только подтвержденную заявку.")

        items=list(rental.items.all())
        device_ids=[i.device_id for i in items]

        devices = {
            device.id: device
            for device in Device.objects
            .select_for_update()
            .filter(id__in=device_ids)
            .order_by("id")
        }

        for item in items:
            device = devices[item.device_id]
            device.quantity_storage += item.quantity
            device.quantity_rented -= item.quantity
            device.is_available = True

        Device.objects.bulk_update(devices.values(), ["quantity_storage", "quantity_rented", "is_available"])
        rental.status = "returned"
        rental.save(update_fields=["status"])
        return rental

class CartService:

    @staticmethod
    def _get_or_create_cart(user_id: int) -> Cart:
        cart, _ = Cart.objects.get_or_create(user_id=user_id)
        return cart

    @staticmethod
    def get(user_id: int):
        cart = CartService._get_or_create_cart(user_id)
        return Device.objects.filter(cartitem__cart=cart)

    @staticmethod
    def add(user_id: int, device_id: int):
        Device.objects.get(id=device_id)  # 404 если нет
        cart = CartService._get_or_create_cart(user_id)
        CartItem.objects.get_or_create(cart=cart, device_id=device_id)
        return CartService.get(user_id)

    @staticmethod
    def remove(user_id: int, device_id: int):
        cart = CartService._get_or_create_cart(user_id)
        CartItem.objects.filter(cart=cart, device_id=device_id).delete()
        return CartService.get(user_id)

    @staticmethod
    def clear(user_id: int):
        cart = CartService._get_or_create_cart(user_id)
        cart.items.all().delete()

