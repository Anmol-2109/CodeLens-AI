from abc import ABC, abstractmethod
from typing import List
import litellm
from app.core.config import settings

class EmbeddingProvider(ABC):
    @abstractmethod
    async def embed_documents(self, documents: List[str]) -> List[List[float]]:
        pass

    @abstractmethod
    async def embed_query(self, query: str) -> List[float]:
        pass

class SentenceTransformerProvider(EmbeddingProvider):
    # We kept the name the same so indexer.py doesn't break, but we swapped the engine!
    def __init__(self, model_name: str = "ollama/nomic-embed-text"):
        self.model_name = model_name

    async def embed_documents(self, documents: List[str]) -> List[List[float]]:
        # Using litellm to talk to local ollama for embeddings! Zero dependencies!
        response = await litellm.aembedding(
            model=self.model_name,
            input=documents,
            api_base=settings.OLLAMA_BASE_URL
        )
        return [data["embedding"] for data in response["data"]]

    async def embed_query(self, query: str) -> List[float]:
        response = await litellm.aembedding(
            model=self.model_name,
            input=[query],
            api_base=settings.OLLAMA_BASE_URL
        )
        return response["data"][0]["embedding"]
