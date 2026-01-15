from __future__ import annotations

from collections.abc import Awaitable, Callable
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.responses import Response

from .api.routers import api_router

SESSION_COOKIE_NAME = "session_id"


def ensure_session_cookie(request: Request, response: Response) -> None:
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    if not session_id:
        response.set_cookie(
            key=SESSION_COOKIE_NAME,
            value=str(uuid4()),
            httponly=True,
            samesite="lax",
        )


def create_app() -> FastAPI:
    app = FastAPI(title="Delivery Service")

    @app.middleware("http")  # type: ignore[misc]
    async def session_middleware(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        response = await call_next(request)
        ensure_session_cookie(request, response)
        return response

    @app.get("/health")  # type: ignore[misc]
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(api_router, prefix="/api")
    return app


app = create_app()
