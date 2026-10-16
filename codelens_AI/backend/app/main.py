from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import auth, repositories, chat, files, webhooks
from app.core.config import settings
from app.db.database import engine, Base
from prometheus_client import make_asgi_app

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-Powered Codebase Intelligence & Developer Copilot",
    version=settings.VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(repositories.router, prefix=f"{settings.API_V1_STR}/repositories", tags=["repositories"])
app.include_router(chat.router, prefix=f"{settings.API_V1_STR}/repositories", tags=["chat"])
app.include_router(files.router, prefix=f"{settings.API_V1_STR}/repositories", tags=["files"])
app.include_router(webhooks.router, prefix=f"{settings.API_V1_STR}/webhooks", tags=["webhooks"])

# Mount prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/health/live")
async def liveness_check():
    return {"status": "alive"}

@app.get("/health/ready")
async def readiness_check():
    return {"status": "ready"}
