from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    specification_template = models.JSONField(default=list)

    def __str__(self):
        return self.name


class Device(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    image = models.ImageField(upload_to="devices/images/", null=True, blank=True)
    documentation = models.FileField(upload_to="devices/docs/", null=True, blank=True)
    doc_text = models.TextField(blank=True, default="")
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="devices"
    )
    manufacturer = models.CharField(max_length=255, blank=True, default="")
    is_available = models.BooleanField(default=True)
    quantity=models.IntegerField(default=0)
    specifications = models.JSONField(default=dict, blank=True)
    embedding = models.JSONField(default=list, blank=True, editable=False)

    def __str__(self):
        return self.name
