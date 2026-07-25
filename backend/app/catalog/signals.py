
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Device
from .services import CatalogService


@receiver(post_save, sender=Device)
def on_device_save(sender, instance, created, **kwargs):
    if instance.documentation and not instance.doc_text:
        CatalogService.store_doc_text(instance)
    CatalogService.store_embedding(instance)