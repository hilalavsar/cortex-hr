from fastapi import FastAPI
from app.core.config import settings
from app.api import auth, chat

app = FastAPI(title=settings.app_name)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")

@app.get("/health")
async def health():
    return {"status": "çalışıyor", "uygulama": settings.app_name}