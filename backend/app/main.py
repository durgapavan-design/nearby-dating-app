import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routers import auth, chat, discovery, matches, profile
from app.core.config import settings

os.makedirs(settings.upload_dir, exist_ok=True)

app = FastAPI(title="Dating App API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(discovery.router)
app.include_router(matches.router)
app.include_router(chat.router)


@app.get("/health")
def health():
    return {"status": "ok"}
