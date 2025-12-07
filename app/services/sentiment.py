# sentiment.py
from abc import ABC, abstractmethod
from typing import List, Tuple
from ..services import sentiment_analysis

class SentimentProvider(ABC):
    @abstractmethod
    def analyze(self, texts: List[str]) -> List[Tuple[str, int]]:
        """Recebe lista de textos e retorna lista de (label, score[0..100])"""

class MockSentimentProvider(SentimentProvider):
    def analyze(self, texts: List[str]) -> List[Tuple[str, int]]:
        results = []
        for t in texts:
            tl = t.lower()
            if any(w in tl for w in ["bom", "ótimo", "maravilhoso", "amei", "perfeito", "gostei"]):
                results.append(("positive", 80))
            elif any(w in tl for w in ["ruim", "péssimo", "horrível", "odiei", "detestei"]):
                results.append(("negative", 80))
            else:
                results.append(("neutral", 50))
        return results