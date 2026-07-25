from django.core.cache import cache
from django.db.models import Q

from app.catalog.models import Device, Category
from app.catalog.parser import DocumentParser
from app.catalog.filters import DeviceFilter
from app.catalog.embedding import EmbeddingService

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
            # search
            search=filters.pop("search",None)
            if search:
                qs=qs.filter(
                    Q(name__icontains=search)|
                    Q(description__icontains=search)
                )
            #filters
            qs = DeviceFilter(qs, filters).apply()
            return qs

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
        category_id = data.pop("category", None)
        device = Device(**data)
        if category_id:
            device.category = Category.objects.get(pk=category_id)
        device.save()
        if device.documentation:
            CatalogService.store_doc_text(device)
        CatalogService.store_embedding(device)
        cache.delete(CACHE_KEY)
        return device

    @staticmethod
    def update(pk: int, data: dict) -> Device:
        device = Device.objects.get(pk=pk)
        old_text = device.get_embedding_text()
        for key, value in data.items():
            setattr(device, key, value)
        device.save()
        if 'documentation' in data and device.documentation:
            CatalogService.store_doc_text(device)
        if device.get_embedding_text() != old_text:
            CatalogService.store_embedding(device)
        cache.delete(CACHE_KEY)
        return Device.objects.select_related("category").get(pk=pk)

    @staticmethod
    def delete(pk: int) -> None:
        Device.objects.filter(pk=pk).delete()
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