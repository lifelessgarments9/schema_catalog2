import heapq
from collections import defaultdict
from django.core.cache import cache

from app.ai.models import ReferenceEmbedding
from app.ai.search import cosine_similarity

import logging
logger = logging.getLogger(__name__)

class QueryAnalyzer:
    TOP_K = 5
    THRESHOLD = 0.60
    CACHE_KEY = "ai:reference_embeddings"
    CACHE_TTL = 60 * 60

    def _reference_embeddings(self):
        refs = cache.get(self.CACHE_KEY)
        logger.info(
            "CACHE CHECK: key=%s, value=%s",
            self.CACHE_KEY,
            "HIT" if refs is not None else "MISS"
        )
        if refs is None:
            refs = [(ref.domain, ref.embedding) for ref in ReferenceEmbedding.objects.all()]
            cache.set(self.CACHE_KEY, refs, self.CACHE_TTL)
            logger.info(
                "CACHE SET: loaded=%d, ttl=%d",
                len(refs),
                self.CACHE_TTL
            )
        return refs

    def analyze(self, query_embedding: list) -> dict:
        scores = defaultdict(list)
        for domain, embedding in self._reference_embeddings():
            similarity = cosine_similarity(query_embedding,embedding,)
            scores[domain].append(similarity)

        averages = {}

        for domain, values in scores.items():
            top_values = heapq.nlargest(self.TOP_K, values)
            averages[domain] = sum(top_values) / len(top_values)

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