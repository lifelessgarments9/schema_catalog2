
from app.catalog.embedding import EmbeddingService
class ContextBuilder:
    def build(self, scored_devices: list) -> str:
        if not scored_devices:
            return "Подходящие устройства не найдены."

        parts = []
        for i, (device, score) in enumerate(scored_devices, 1):
            text = EmbeddingService.build_device_text(device, doc_limit=1500)
            parts.append(f"Устройство {i} (релевантность: {score:.0%})\n{text}")

        return "\n\n".join(parts)
