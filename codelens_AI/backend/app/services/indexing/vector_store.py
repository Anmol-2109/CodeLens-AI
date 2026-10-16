from typing import List, Dict, Any
from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models as rest
import uuid

from app.core.config import settings

class VectorStore:
    def __init__(self):
        self.client = AsyncQdrantClient(url=settings.QDRANT_URL)
        self.collection_name = "code_chunks"

    async def ensure_collection_exists(self, vector_size: int = 384):
        collections = await self.client.get_collections()
        exists = any(c.name == self.collection_name for c in collections.collections)
        
        if not exists:
            await self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=rest.VectorParams(
                    size=vector_size,
                    distance=rest.Distance.COSINE
                )
            )
            # Create payload indices for fast filtering by repository
            await self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="repository_id",
                field_schema=rest.PayloadSchemaType.INTEGER
            )

    async def upsert_chunks(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]):
        points = []
        for chunk, vector in zip(chunks, embeddings):
            points.append(
                rest.PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vector,
                    payload=chunk
                )
            )
        
        await self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

    async def search(self, query_vector: List[float], repository_id: int, top_k: int = 30) -> List[Dict[str, Any]]:
        search_result = await self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            query_filter=rest.Filter(
                must=[
                    rest.FieldCondition(
                        key="repository_id",
                        match=rest.MatchValue(value=repository_id)
                    )
                ]
            ),
            limit=top_k
        )
        
        return [
            {
                "id": hit.id,
                "score": hit.score,
                "payload": hit.payload
            }
            for hit in search_result
        ]
