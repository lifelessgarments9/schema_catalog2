from datetime import date
from django.db import transaction

from app.catalog.models import Device
from app.rental.models import Cart, CartItem, RentalRequest, RentalRequestItem
from app.rental.pdf import PdfService

class RentalRequestService:

    @staticmethod
    def get_requests(user):
        qs = RentalRequest.objects.prefetch_related("items", "items__device").order_by("-created_at")
        return qs.all() if user.is_staff else qs.filter(student=user)

    @staticmethod
    @transaction.atomic
    def create(student, data):
        items_data = data.pop("items")
        device_ids = [item["device"].id for item in items_data]
        devices = {
            device.id: device
            for device in Device.objects.select_for_update().filter(
                id__in=device_ids
            )
        }

        for item in items_data:
            device = devices[item["device"].id]
            if device.quantity < item["quantity"]:
                raise ValueError(f"Недостаточно «{device.name}» на складе.")

        rental = RentalRequest.objects.create(student=student,**data)
        rental_items = []
        for item in items_data:
            device = devices[item["device"].id]
            device.quantity -= item["quantity"]
            device.is_available = device.quantity > 0
            device.save(update_fields=["quantity", "is_available"])
            rental_items.append(
                RentalRequestItem(
                    request=rental,
                    device=device,
                    quantity=item["quantity"],
                    return_date=item["return_date"],
                )
            )
        RentalRequestItem.objects.bulk_create(rental_items)
        CartService.clear(student.id)
        return rental

    @staticmethod
    @transaction.atomic
    def approve(request_id):
        rental = RentalRequest.objects.prefetch_related(
            "items", "items__device"
        ).get(pk=request_id)

        if rental.status != "pending":
            raise ValueError("Заявка уже обработана.")

        rental.status = "approved"
        rental.issue_date = date.today()
        rental.save()
        return rental

    @staticmethod
    @transaction.atomic
    def delete(request_id):
        rental = RentalRequest.objects.select_for_update().prefetch_related(
            "items",
            "items__device"
        ).get(pk=request_id)

        if rental.status == "approved":
            raise ValueError("Нельзя удалить подтвержденную заявку.")

        for item in rental.items.all():
            device = Device.objects.select_for_update().get(
                pk=item.device_id
            )
            device.quantity += item.quantity
            device.is_available = True
            device.save(update_fields=["quantity", "is_available"])
        rental.delete()

    @staticmethod
    @transaction.atomic
    def return_devices(request_id):
        rental = RentalRequest.objects.prefetch_related(
            "items",
            "items__device"
        ).get(pk=request_id)
        if rental.status != "approved":
            raise ValueError("Вернуть можно только подтвержденную заявку.")
        for item in rental.items.all():
            device = item.device
            device.quantity += item.quantity
            device.is_available = True
            device.save(update_fields=["quantity", "is_available"])

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

