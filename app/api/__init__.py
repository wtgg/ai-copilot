from fastapi import APIRouter

from app.api.v1 import api_v1

apis = APIRouter(prefix='/api')

apis.include_router(api_v1)
