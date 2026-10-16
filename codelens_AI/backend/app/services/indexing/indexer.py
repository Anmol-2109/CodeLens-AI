import os
import shutil
import tempfile
import git
import asyncio
from typing import List, Dict, Any
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.models.repository import Repository, RepositoryStatus
from app.db.models.chunk import File, CodeChunk
from app.code_analysis.parser.tree_sitter_parser import PythonParser, JavaParser
from app.services.indexing.vector_store import VectorStore
from app.ai.embeddings.provider import SentenceTransformerProvider

class RepositoryIndexer:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.vector_store = VectorStore()
        self.embedding_provider = SentenceTransformerProvider()
        self.parsers = {
            ".py": PythonParser(),
            ".java": JavaParser()
        }
        
    async def index_repository(self, repo_id: int):
        # 1. Fetch Repository from DB
        result = await self.db.execute(select(Repository).where(Repository.id == repo_id))
        repo = result.scalars().first()
        if not repo:
            raise ValueError(f"Repository {repo_id} not found.")

        # Update status
        repo.status = RepositoryStatus.INDEXING
        await self.db.commit()

        temp_dir = tempfile.mkdtemp()
        try:
            # 2. Clone Repository
            print(f"Cloning {repo.github_url} to {temp_dir}...")
            await asyncio.to_thread(git.Repo.clone_from, repo.github_url, temp_dir)

            # Ensure Qdrant collection exists for 768 dim vectors (nomic-embed-text)
            await self.vector_store.ensure_collection_exists(vector_size=768)

            # 3. Walk Files and Parse
            all_chunks_payload = []
            all_chunks_text = []

            for root, _, files in os.walk(temp_dir):
                # Skip .git directory
                if ".git" in root:
                    continue
                    
                for file_name in files:
                    # Yield to event loop to prevent blocking during intensive parsing
                    await asyncio.sleep(0)
                    
                    file_path = os.path.join(root, file_name)
                    ext = Path(file_path).suffix
                    
                    if ext in self.parsers:
                        relative_path = os.path.relpath(file_path, temp_dir)
                        
                        # Read file content
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            source_code = f.read()
                        
                        # Create File Record
                        db_file = File(
                            repository_id=repo.id,
                            file_path=relative_path,
                            language=ext,
                            content_hash=str(hash(source_code)) # Simple hash for now
                        )
                        self.db.add(db_file)
                        await self.db.flush() # To get db_file.id

                        # Parse AST
                        parser = self.parsers[ext]
                        tree = parser.parse(source_code)
                        symbols = parser.extract_symbols(tree, source_code)

                        # Create Code Chunks
                        lines = source_code.splitlines()
                        for sym in symbols:
                            start_l, end_l = sym["start_line"], sym["end_line"]
                            chunk_text = "\n".join(lines[start_l:end_l+1])
                            
                            db_chunk = CodeChunk(
                                file_id=db_file.id,
                                symbol_name=sym["name"],
                                symbol_type=sym["type"],
                                start_line=start_l + 1, # 1-indexed
                                end_line=end_l + 1,
                                chunk_content=chunk_text
                            )
                            self.db.add(db_chunk)
                            await self.db.flush()
                            
                            # Prepare for Vectorization
                            payload = {
                                "repository_id": repo.id,
                                "file_id": db_file.id,
                                "file_path": relative_path,
                                "chunk_id": db_chunk.id,
                                "symbol_name": sym["name"],
                                "symbol_type": sym["type"],
                                "chunk_content": chunk_text
                            }
                            all_chunks_payload.append(payload)
                            
                            # We embed a combination of the path and the code for better semantic meaning
                            enrich_text = f"File: {relative_path}\nType: {sym['type']}\nName: {sym['name']}\nCode:\n{chunk_text}"
                            all_chunks_text.append(enrich_text)

            # 4. Generate Embeddings and Upload to Vector Store
            if all_chunks_text:
                print(f"Generating embeddings for {len(all_chunks_text)} chunks...")
                embeddings = await self.embedding_provider.embed_documents(all_chunks_text)
                
                print("Uploading to Qdrant...")
                await self.vector_store.upsert_chunks(all_chunks_payload, embeddings)

            repo.status = RepositoryStatus.COMPLETED
            await self.db.commit()
            print(f"Repository {repo.id} indexing completed successfully.")

        except Exception as e:
            repo.status = RepositoryStatus.FAILED
            await self.db.commit()
            print(f"Indexing failed: {e}")
            raise e
        finally:
            shutil.rmtree(temp_dir)
