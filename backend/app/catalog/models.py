from django.db import models
from django.db.models import F


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Specification(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="specifications"
    )
    name = models.CharField(max_length=200)

    class Meta:
        unique_together = ("category", "name")
        ordering = ["name"]

    def __str__(self):
        return f"{self.category.name} → {self.name}"


class Device(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    image = models.ImageField(upload_to="devices/images/", null=True, blank=True)
    documentation = models.FileField(upload_to="devices/docs/", null=True, blank=True)
    doc_text = models.TextField(blank=True, default="")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="devices")
    manufacturer = models.CharField(max_length=255, blank=True, default="",verbose_name="storage")
    is_available = models.BooleanField(default=True)
    quantity = models.PositiveIntegerField(default=0)
    quantity_storage = models.PositiveIntegerField(default=0)
    quantity_rented = models.PositiveIntegerField(default=0)
    specifications = models.JSONField(default=dict, blank=True)
    embedding = models.JSONField(default=list, blank=True, editable=False)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(quantity=F("quantity_storage") + F("quantity_rented")),
                name="quantity_equals_storage_plus_rented",
            ),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.quantity = self.quantity_storage + self.quantity_rented
        self.is_available = self.quantity_storage > 0
        super().save(*args, **kwargs)
