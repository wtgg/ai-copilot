from fastapi import APIRouter

from app.api.v1 import chat, upload

api_v1 = APIRouter(prefix='/v1')
api_v1.include_router(chat.router)
api_v1.include_router(upload.router)

