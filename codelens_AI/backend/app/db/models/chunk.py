from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class File(Base):
    __tablename__ = "repository_files"

    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"), nullable=False)
    file_path = Column(String, index=True, nullable=False)
    language = Column(String, nullable=True)
    content_hash = Column(String, nullable=False)
    
    repository = relationship("Repository", backref="files")

class CodeChunk(Base):
    __tablename__ = "code_chunks"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("repository_files.id"), nullable=False)
    symbol_name = Column(String, nullable=True)
    symbol_type = Column(String, nullable=True)
    start_line = Column(Integer, nullable=False)
    end_line = Column(Integer, nullable=False)
    chunk_content = Column(String, nullable=False)
    
    file = relationship("File", backref="chunks")
