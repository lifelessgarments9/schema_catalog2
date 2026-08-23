import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from app.ai.models import ReferenceEmbedding
from app.ai.reference_examples import GENERAL_EXAMPLES
from app.ai.embeddings import EmbeddingService


def main():
    embedding_service = EmbeddingService()

    created = 0
    skipped = 0

    for text in GENERAL_EXAMPLES:
        text = text.strip()

        if not text:
            continue

        if ReferenceEmbedding.objects.filter(text=text).exists():
            skipped += 1
            continue

        embedding = embedding_service.embed(text)

        ReferenceEmbedding.objects.create(
            text=text,
            domain="general",
            embedding=embedding,
        )

        created += 1
        print(f"Добавлено: {text}")

    print()
    print(f"Готово.")
    print(f"Добавлено: {created}")
    print(f"Пропущено: {skipped}")


if __name__ == "__main__":
    main()