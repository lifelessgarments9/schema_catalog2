import math


def cosine_similarity(a: list, b: list) -> float:
    """Вычислить косинусное сходство двух векторов."""
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class DeviceSearcher:

    TOP_K = 3

    def search(self, query_embedding: list, top_k: int = None) -> list:
        from app.catalog.models import Device

        if top_k is None or top_k>5:
            top_k = self.TOP_K

        devices = Device.objects.filter(is_available=True).exclude(embedding=[])

        scored = []
        for device in devices:
            emb = device.embedding
            if not emb:
                continue
            score = cosine_similarity(query_embedding, emb)
            scored.append((device, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]
