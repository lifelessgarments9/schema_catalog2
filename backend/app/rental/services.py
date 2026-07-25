from datetime import date
import io
import os

from django.core.files.base import ContentFile
from django.db import transaction

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from app.catalog.models import Device
from app.rental.models import Cart, CartItem, RentalRequest, RentalRequestItem

class PdfService:
    _registered = False
    font_paths = [
        (
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ),
        (
            r"C:\Windows\Fonts\arial.ttf",
            r"C:\Windows\Fonts\arialbd.ttf",
        ),
    ]

    @classmethod
    def register_fonts(cls):
        if cls._registered: return
        for regular, bold in cls.font_paths:
            if os.path.exists(regular) and os.path.exists(bold):
                pdfmetrics.registerFont(TTFont("Regular", regular))
                pdfmetrics.registerFont(TTFont("Bold", bold))
                cls._registered = True
                return
        raise RuntimeError("Не найден шрифт для PDF.")

    @staticmethod
    def generate(request)-> ContentFile:
        PdfService.register_fonts()
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        y = 800
        def write(text, font="Regular", size=11):
            nonlocal y
            pdf.setFont(font, size)
            pdf.drawString(40, y, text)
            y -= 20
        write(f"Заявка №{request.pk}", "Bold", 14)
        write(f"ФИО: {request.full_name}")
        write(f"Группа: {request.group}")
        write(f"Дисциплина: {request.discipline}")
        write(f"Дата выдачи: {request.issue_date}")
        write(f"Статус: {request.get_status_display()}")
        y -= 10
        write("Состав заявки", "Bold")
        for item in request.items.select_related("device"):
            write(
                f"{item.device.name} × {item.quantity} "
                f"(до {item.return_date})"
            )
        pdf.save()
        buffer.seek(0)
        return ContentFile(buffer.read(),name=f"request_{request.pk}.pdf")


class RentalRequestService:

    @staticmethod
    def get_requests(user):
        qs = RentalRequest.objects.prefetch_related("items", "items__device").order_by("-id")
        return qs.all() if user.is_staff else qs.filter(student=user)

    @staticmethod
    @transaction.atomic
    def create(student, data):
        items_data = data.pop("items")
        rental = RentalRequest.objects.create(student=student, **data)
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
        rental = RentalRequest.objects.prefetch_related(
            "items", "items__device"
        ).get(pk=request_id)

        if rental.status != "pending":
            raise ValueError("Заявка уже обработана.")

        # Проверяем остатки одним проходом
        for item in rental.items.all():
            if item.device.quantity < item.quantity:
                raise ValueError(f"Недостаточно «{item.device.name}» на складе.")

        # Списываем устройства
        for item in rental.items.all():
            device = item.device
            device.quantity -= item.quantity
            device.is_available = device.quantity > 0
            device.save()

        rental.status = "approved"
        rental.issue_date = date.today()
        pdf = PdfService.generate(rental)
        rental.pdf.save(pdf.name,pdf,save=False)
        rental.save()
        return rental

    @staticmethod
    def delete(request_id):
        rental = RentalRequest.objects.get(pk=request_id)
        if rental.status == "approved":
            raise ValueError("Нельзя удалить подтвержденную заявку.")
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