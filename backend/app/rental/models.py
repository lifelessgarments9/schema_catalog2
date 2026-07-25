from django.db import models

from app.accounts.models import User
from app.catalog.models import Device


class RentalRequest(models.Model):
    STATUS_CHOICES = [
        ("pending",  "Ожидает"),
        ("approved", "Подтверждена"),
        ("rejected", "Отклонена"),
        ("returned", "Возвращена")
    ]

    student    = models.ForeignKey(User, on_delete=models.CASCADE, related_name="requests")
    full_name  = models.CharField(max_length=255)
    group      = models.CharField(max_length=50)
    discipline = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    issue_date = models.DateField(null=True, blank=True)
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    pdf        = models.FileField(upload_to="requests/pdf/", null=True, blank=True)

    def __str__(self):
        return f"#{self.pk} {self.full_name} [{self.status}]"


class RentalRequestItem(models.Model):
    request     = models.ForeignKey(RentalRequest, on_delete=models.CASCADE, related_name="items")
    device      = models.ForeignKey(Device, on_delete=models.PROTECT)
    quantity    = models.PositiveIntegerField()
    return_date = models.DateField()


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cart")


class CartItem(models.Model):
    cart     = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    device   = models.ForeignKey(Device, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("cart", "device")