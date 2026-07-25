import json
import ollama


class EmbeddingService:
    MODEL = "nomic-embed-text"

    @classmethod
    def create(cls, text: str) -> list:
        response = ollama.embed(model=cls.MODEL, input=text)
        return response["embeddings"][0]

    @classmethod
    def build_device_text(cls, device, doc_limit: int = 2000) -> str:
        parts = []

        if device.name:
            parts.append(f"Название: {device.name}")
        if device.description:
            parts.append(f"Описание: {device.description}")
        if device.specifications:
            specs = device.specifications
            if isinstance(specs, str):
                try:
                    specs = json.loads(specs)
                except (TypeError, ValueError):
                    specs = {}
            specs_text = "; ".join(f"{k}: {v}" for k, v in specs.items())
            parts.append(f"Характеристики: {specs_text}")
        if device.doc_text:
            parts.append(f"Документация:\n{device.doc_text[:doc_limit]}")

        return "\n".join(parts)

    @classmethod
    def create_for_device(cls, device) -> list:
        text = cls.build_device_text(device)
        if not text.strip():
            return []
        return cls.create(text)