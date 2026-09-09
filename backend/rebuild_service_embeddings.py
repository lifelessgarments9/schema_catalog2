import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from app.ai.models import ReferenceEmbedding
from app.ai.reference_examples import SERVICE_EXAMPLES
from app.catalog.embedding import EmbeddingService


def rebuild_service_domain():

    # 1. Удалить все записи домена service
    deleted_count, _ = ReferenceEmbedding.objects.filter(domain="service").delete()
    print(f"🗑 Удалено {deleted_count} старых service-эталонов")

    # 2. Создать новые
    created = 0
    for phrase in SERVICE_EXAMPLES:
        embedding = EmbeddingService.create(phrase)
        ReferenceEmbedding.objects.create(
            domain="service",
            text=phrase,
            embedding=embedding,
        )
        created += 1
        print(f"  ✓ [{created}] {phrase[:60]}")

    print(f"\n✅ Готово! Создано {created} service-эталонов")


if __name__ == "__main__":
    rebuild_service_domain()