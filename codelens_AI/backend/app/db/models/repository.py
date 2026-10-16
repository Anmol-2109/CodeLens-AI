from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.db.database import Base

class RepositoryStatus(str, enum.Enum):
    PENDING = "PENDING"
    INDEXING = "INDEXING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Repository(Base):
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    github_url = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    default_branch = Column(String, default="main")
    status = Column(Enum(RepositoryStatus), default=RepositoryStatus.PENDING)
    last_indexed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    owner = relationship("User")
