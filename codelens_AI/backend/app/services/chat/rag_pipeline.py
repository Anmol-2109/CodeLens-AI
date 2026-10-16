from typing import AsyncGenerator
from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models as rest
from app.ai.llm.provider import LiteLLMProvider
from app.ai.embeddings.provider import SentenceTransformerProvider
from app.core.config import settings
import json

class RAGPipeline:
    def __init__(self, llm: LiteLLMProvider, embedding: SentenceTransformerProvider, qdrant_client=None):
        self.llm = llm
        self.embedding = embedding
        self.qdrant = qdrant_client or AsyncQdrantClient(url=settings.QDRANT_URL)
        
    async def answer_query(self, query: str, repo_id: int) -> AsyncGenerator[str, None]:
        # 1. Embed Query
        query_vectors = await self.embedding.embed_documents([query])
        query_vector = query_vectors[0]

        # 2. Retrieve from Qdrant
        search_result = await self.qdrant.search(
            collection_name="code_chunks",
            query_vector=query_vector,
            query_filter=rest.Filter(
                must=[
                    rest.FieldCondition(
                        key="repository_id",
                        match=rest.MatchValue(value=repo_id)
                    )
                ]
            ),
            limit=5
        )

        # 3. Construct Context
        context_blocks = []
        for hit in search_result:
            p = hit.payload
            # Extract metadata safely
            file_path = p.get('file_path', 'Unknown')
            sym_name = p.get('symbol_name', 'Unknown')
            # Assuming chunk_content was saved, otherwise we'd fetch it from DB
            chunk_content = p.get('chunk_content', '') 
            
            context_blocks.append(f"--- File: {file_path} | Symbol: {sym_name} ---\n{chunk_content}")

        context_str = "\n\n".join(context_blocks)
        if not context_str.strip():
            context_str = "No relevant code found in this repository for the given query."

        # 4. Construct Prompt
        system_prompt = (
            "You are an expert Senior Software Engineer and Codebase Intelligence Copilot. "
            "Use the provided codebase context to answer the user's question accurately. "
            "If the answer is not in the context, say you don't know based on the current context."
        )
        
        user_prompt = f"Context:\n{context_str}\n\nQuestion: {query}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        # 5. Stream LLM Response
        async for token in self.llm.stream(messages=messages):
            yield token
