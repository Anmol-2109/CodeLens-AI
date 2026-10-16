from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
import hashlib
import hmac
from app.core.config import settings
from app.services.indexing.indexer import RepositoryIndexer
from app.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models.repository import Repository

router = APIRouter()

# This is a stub for verifying GitHub webhooks
def verify_github_signature(request: Request, body: bytes, secret: str) -> bool:
    signature_header = request.headers.get("x-hub-signature-256")
    if not signature_header:
        return False
        
    hash_object = hmac.new(secret.encode("utf-8"), msg=body, digestmod=hashlib.sha256)
    expected_signature = "sha256=" + hash_object.hexdigest()
    
    return hmac.compare_digest(expected_signature, signature_header)

@router.post("/github")
async def github_webhook(request: Request, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    # 1. Read Payload
    payload = await request.json()
    
    # Optional: Verify webhook signature (Requires WEBHOOK_SECRET in .env)
    # raw_body = await request.body()
    # if not verify_github_signature(request, raw_body, settings.GITHUB_WEBHOOK_SECRET):
    #     raise HTTPException(status_code=403, detail="Invalid signature")
        
    # 2. Check if it's a push event
    event_type = request.headers.get("x-github-event")
    if event_type == "ping":
        return {"msg": "pong"}
        
    if event_type == "push":
        repo_data = payload.get("repository", {})
        clone_url = repo_data.get("clone_url")
        
        if not clone_url:
            return {"msg": "No clone URL found in payload"}
            
        # 3. Find matching repository in DB
        result = await db.execute(select(Repository).where(Repository.github_url == clone_url))
        repo = result.scalars().first()
        
        if repo:
            # 4. Trigger Re-indexing in Background
            indexer = RepositoryIndexer(db=db)
            background_tasks.add_task(indexer.index_repository, repo.id)
            return {"msg": f"Triggered re-index for {repo.name}"}
            
    return {"msg": "Ignored"}
