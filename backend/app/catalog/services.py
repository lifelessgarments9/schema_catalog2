from django.core.cache import cache

from app.catalog.models import Device, Category
from app.catalog.parser import DocumentParser
from app.catalog.filters import DeviceFilter
from app.catalog.embedding import EmbeddingService
from django.shortcuts import get_object_or_404

CACHE_KEY = "catalog:all"
CACHE_TTL = 3000


class CatalogService:
    @staticmethod
    def get_all(filters: dict = None):
        if not filters:
            cached = cache.get(CACHE_KEY)
            if cached is not None:
                return cached

        qs = Device.objects.select_related("category").all()

        if filters:
            return DeviceFilter(qs,filters).apply()

        result = list(qs)
        cache.set(CACHE_KEY, result, CACHE_TTL)
        return result

    @staticmethod
    def get(pk: int) -> Device:
        return Device.objects.select_related("category").get(pk=pk)

    @staticmethod
    def get_categories():
        return Category.objects.all()

    @staticmethod
    def create(data: dict) -> Device:
        values=data.copy()
        category = values.pop("category")
        device = Device(**data)
        device.category = category
        device.save()
        cache.delete(CACHE_KEY)
        return device

    @staticmethod
    def update(pk: int, data: dict) -> Device:
        device = Device.objects.get(pk=pk)
        old_text = device.get_embedding_text()
        for key, value in data.items():
            setattr(device, key, value)
        device.save()
        cache.delete(CACHE_KEY)
        return Device.objects.select_related("category").get(pk=pk)

    @staticmethod
    def delete(pk: int) -> None:
        get_object_or_404(Device, pk=pk).delete()
        cache.delete(CACHE_KEY)

    @staticmethod
    def store_doc_text(device: Device) -> None:
        text = DocumentParser.parse(device.documentation.path)
        Device.objects.filter(pk=device.pk).update(doc_text=text)
        device.doc_text = text

    @staticmethod
    def store_embedding(device: Device):
        embedding = EmbeddingService.create_for_device(device)
        if not embedding:
            return
        Device.objects.filter(pk=device.pk).update(embedding=embedding)
        device.embedding = embedding
