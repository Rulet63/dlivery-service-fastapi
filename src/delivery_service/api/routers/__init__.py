from fastapi import APIRouter

from .package_types import router as package_types_router

api_router = APIRouter()
api_router.include_router(package_types_router)
