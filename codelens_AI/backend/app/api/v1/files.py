from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pathlib import Path
import httpx

from app.db.database import get_db
from app.db.models.user import User
from app.db.models.repository import Repository
from app.db.models.chunk import File
from app.api.dependencies import get_current_user

router = APIRouter()

@router.get("/{repo_id}/files")
async def get_files(
    repo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Repository).where(Repository.id == repo_id, Repository.owner_id == current_user.id))
    repo = result.scalars().first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
        
    result = await db.execute(select(File).where(File.repository_id == repo_id))
    files = result.scalars().all()
    
    return [{"id": f.id, "file_path": f.file_path, "language": f.language} for f in files]

@router.get("/{repo_id}/files/content")
async def get_file_content(
    repo_id: int,
    file_path: str = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Security check: Ensure user owns repository
    result = await db.execute(select(Repository).where(Repository.id == repo_id, Repository.owner_id == current_user.id))
    repo = result.scalars().first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    # Convert github url to raw url
    # e.g. https://github.com/owner/repo -> https://raw.githubusercontent.com/owner/repo/main/filepath
    base_url = repo.github_url
    if base_url.endswith(".git"):
        base_url = base_url[:-4]
    
    raw_base = base_url.replace("github.com", "raw.githubusercontent.com")
    branch = repo.default_branch or "main"
    
    raw_url = f"{raw_base}/{branch}/{file_path}"
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(raw_url)
            if resp.status_code == 200:
                content = resp.text
            else:
                content = f"// Error fetching file: {resp.status_code}\n// URL: {raw_url}"
    except Exception as e:
        content = f"// Error fetching file: {str(e)}"

    return {"file_path": file_path, "content": content}
