from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.database import get_db
from app.db.models.user import User
from app.db.models.repository import Repository
from app.api.dependencies import get_current_user
from app.services.chat.rag_pipeline import RAGPipeline
from app.ai.llm.provider import LiteLLMProvider
from app.ai.embeddings.provider import SentenceTransformerProvider
from app.core.config import settings

router = APIRouter()

class ChatRequest(BaseModel):
    query: str
    conversation_id: int | None = None

async def get_rag_pipeline() -> RAGPipeline:
    # In a real app, this should be a singleton or properly managed dependency
    llm = LiteLLMProvider(model_name=f"ollama/{settings.LLM_MODEL}", api_base=settings.OLLAMA_BASE_URL)
    embedding = SentenceTransformerProvider(model_name="ollama/nomic-embed-text")
    return RAGPipeline(llm=llm, embedding=embedding, qdrant_client=None)

@router.post("/{repo_id}/chat")
async def chat(
    repo_id: int,
    chat_req: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rag: RAGPipeline = Depends(get_rag_pipeline)
):
    # Verify access to repository
    result = await db.execute(select(Repository).where(Repository.id == repo_id, Repository.owner_id == current_user.id))
    repo = result.scalars().first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    import json
    
    async def event_generator():
        try:
            yield f'data: {json.dumps({"event": "message_start"})}\n\n'
            
            async for token in rag.answer_query(query=chat_req.query, repo_id=repo_id):
                yield f'data: {json.dumps({"event": "token", "text": token})}\n\n'
                
            yield f'data: {json.dumps({"event": "message_complete"})}\n\n'
        except Exception as e:
            yield f'data: {json.dumps({"event": "error", "text": str(e)})}\n\n'

    return StreamingResponse(event_generator(), media_type="text/event-stream")
