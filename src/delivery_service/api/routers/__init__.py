from fastapi import APIRouter

from .debug import router as debug_router
from .package_types import router as package_types_router
from .packages import router as packages_router

api_router = APIRouter()
api_router.include_router(package_types_router)
api_router.include_router(packages_router)
api_router.include_router(debug_router)
