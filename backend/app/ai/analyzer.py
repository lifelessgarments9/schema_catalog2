from collections import defaultdict

from app.ai.models import ReferenceEmbedding
from app.ai.search import cosine_similarity
from app.catalog.embedding import EmbeddingService


class QueryAnalyzer:

    THRESHOLD = 0.60

    def analyze(self, query_embedding: list) -> dict:
        scores = defaultdict(list)
        for ref in ReferenceEmbedding.objects.all():
            similarity = cosine_similarity(query_embedding,ref.embedding,)
            scores[ref.domain].append(similarity)

        averages = {}

        for domain, values in scores.items():
            averages[domain] = sum(values) / len(values)

        best_domain = max(averages, key=averages.get)
        best_score = averages[best_domain]

        if best_score < self.THRESHOLD:
            best_domain = "general"

        return {
            "domain": best_domain,
            "score": round(best_score, 3),
            "details": {
                domain: round(score, 3)
                for domain, score in averages.items()
            }
        }