from pydantic import BaseModel, HttpUrl
from datetime import datetime
from app.db.models.repository import RepositoryStatus

class RepositoryBase(BaseModel):
    name: str
    github_url: HttpUrl
    default_branch: str = "main"

class RepositoryCreate(RepositoryBase):
    pass

class RepositoryResponse(RepositoryBase):
    id: int
    owner_id: int
    status: RepositoryStatus
    last_indexed_at: datetime | None
    created_at: datetime | None

    class Config:
        from_attributes = True
