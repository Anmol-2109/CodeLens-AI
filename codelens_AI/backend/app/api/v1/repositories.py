from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
import asyncio

from app.db.database import get_db, AsyncSessionLocal
from app.db.models.repository import Repository, RepositoryStatus
from app.db.models.user import User
from app.schemas.repository import RepositoryCreate, RepositoryResponse
from app.api.dependencies import get_current_user
from app.services.indexing.indexer import RepositoryIndexer

router = APIRouter()

async def run_indexing_task(repo_id: int):
    async with AsyncSessionLocal() as db:
        indexer = RepositoryIndexer(db)
        try:
            await indexer.index_repository(repo_id)
        except Exception as e:
            print(f"Background indexing task failed: {e}")

@router.get("/", response_model=List[RepositoryResponse])
async def list_repositories(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Repository).where(Repository.owner_id == current_user.id))
    return result.scalars().all()

@router.post("/", response_model=RepositoryResponse)
async def create_repository(
    repo_in: RepositoryCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_repo = Repository(
        name=repo_in.name,
        github_url=str(repo_in.github_url),
        default_branch=repo_in.default_branch,
        owner_id=current_user.id,
        status=RepositoryStatus.PENDING
    )
    db.add(db_repo)
    await db.commit()
    await db.refresh(db_repo)
    
    # Trigger indexing in background
    background_tasks.add_task(run_indexing_task, db_repo.id)
    
    return db_repo

@router.get("/{repo_id}", response_model=RepositoryResponse)
async def get_repository(
    repo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Repository).where(Repository.id == repo_id, Repository.owner_id == current_user.id)
    )
    repo = result.scalars().first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    return repo

@router.post("/{repo_id}/sync", response_model=RepositoryResponse)
async def sync_repository(
    repo_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Repository).where(Repository.id == repo_id, Repository.owner_id == current_user.id)
    )
    repo = result.scalars().first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    # Re-trigger indexing
    background_tasks.add_task(run_indexing_task, repo.id)
    return repo

@router.delete("/{repo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_repository(
    repo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Repository).where(Repository.id == repo_id, Repository.owner_id == current_user.id)
    )
    repo = result.scalars().first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    # Manual cascade delete for files and chunks
    from app.db.models.chunk import File, CodeChunk
    from sqlalchemy import delete
    
    # 1. Delete code chunks belonging to the repository's files
    files_result = await db.execute(select(File.id).where(File.repository_id == repo_id))
    file_ids = files_result.scalars().all()
    if file_ids:
        await db.execute(delete(CodeChunk).where(CodeChunk.file_id.in_(file_ids)))
    
    # 2. Delete the files
    await db.execute(delete(File).where(File.repository_id == repo_id))
    
    # 3. Delete the repository
    await db.delete(repo)
    await db.commit()
