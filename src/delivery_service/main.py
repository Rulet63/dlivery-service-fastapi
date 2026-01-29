from __future__ import annotations

import logging
import time
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response

from .api.routers import api_router
from .utils.redis_client import close_redis

SESSION_COOKIE_NAME = "session_id"
logger = logging.getLogger("delivery_service.web")


def error_payload(
    *, error_code: str, message: str, details: object | None = None
) -> dict[str, object]:
    return {
        "error_code": error_code,
        "message": message,
        "details": details if details is not None else {},
    }


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield
    await close_redis()


def create_app() -> FastAPI:
    app = FastAPI(title="Delivery Service", redirect_slashes=False, lifespan=lifespan)

    @app.exception_handler(HTTPException)  # type: ignore[misc]
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        detail = exc.detail

        if isinstance(detail, dict) and "error_code" in detail and "message" in detail:
            payload = dict(detail)
            payload.setdefault("details", {"path": request.url.path})
            return JSONResponse(status_code=exc.status_code, content=payload)

        if isinstance(detail, (dict, list)):
            payload = error_payload(error_code="http_error", message="HTTP error", details=detail)
        else:
            payload = error_payload(
                error_code="http_error",
                message=str(detail),
                details={"path": request.url.path},
            )

        return JSONResponse(status_code=exc.status_code, content=payload)

    @app.exception_handler(RequestValidationError)  # type: ignore[misc]
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        payload = error_payload(
            error_code="validation_error",
            message="Request validation failed",
            details=exc.errors(),
        )
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=payload)

    @app.exception_handler(Exception)  # type: ignore[misc]
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception")
        payload = error_payload(
            error_code="internal_error",
            message="Internal server error",
            details={"path": request.url.path},
        )
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=payload)

    @app.middleware("http")  # type: ignore[misc]
    async def session_middleware(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        raw_session_id = request.cookies.get(SESSION_COOKIE_NAME)
        session_id = raw_session_id or str(uuid4())
        request.state.session_id = session_id

        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000

        logger.info(
            "request method=%s url=%s status=%s duration_ms=%.2f session_id=%s",
            request.method,
            str(request.url),
            response.status_code,
            duration_ms,
            session_id,
        )

        if not raw_session_id:
            response.set_cookie(
                key=SESSION_COOKIE_NAME,
                value=session_id,
                httponly=True,
                samesite="lax",
                path="/",
            )

        return response

    @app.get("/health")  # type: ignore[misc]
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(api_router, prefix="/api")
    return app


app = create_app()
