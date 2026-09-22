from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import Device, Specification
from .services import CatalogService


@receiver(post_save, sender=Device)
def on_device_save(sender, instance, created, **kwargs):
    if instance.documentation and not instance.doc_text:
        CatalogService.store_doc_text(instance)

    CatalogService.store_embedding(instance)


@receiver(post_save, sender=Specification)
def add_specification_to_devices(sender, instance, created, **kwargs):
    if not created:
        return

    devices = Device.objects.filter(category=instance.category)

    for device in devices:
        specifications = device.specifications or {}

        if instance.name not in specifications:
            specifications[instance.name] = ""

            Device.objects.filter(pk=device.pk).update(
                specifications=specifications
            )

@receiver(post_delete, sender=Specification)
def remove_specification_from_devices(sender, instance, **kwargs):
    devices = Device.objects.filter(category=instance.category)

    for device in devices:
        specifications = device.specifications or {}

        if instance.name in specifications:
            specifications.pop(instance.name)

            Device.objects.filter(pk=device.pk).update(
                specifications=specifications
            )