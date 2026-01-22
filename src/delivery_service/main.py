from __future__ import annotations

import logging
import time
from collections.abc import Awaitable, Callable
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response

from .api.routers import api_router
from .config import settings

SESSION_COOKIE_NAME = "session_id"

log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

logging.basicConfig(
    level=log_level,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    force=True,
)

logging.getLogger().setLevel(log_level)
logging.getLogger("delivery_service").setLevel(log_level)

logger = logging.getLogger("delivery_service.web")


def error_payload(
    *, error_code: str, message: str, details: object | None = None
) -> dict[str, object]:
    return {
        "error_code": error_code,
        "message": message,
        "details": details if details is not None else {},
    }


def create_app() -> FastAPI:
    app = FastAPI(title="Delivery Service", redirect_slashes=False)

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
        session_id = request.cookies.get(SESSION_COOKIE_NAME) or str(uuid4())
        request.state.session_id = session_id

        start = time.perf_counter()
        response: Response | None = None

        try:
            response = await call_next(request)
        except Exception:
            logger.exception(
                "Unhandled exception during request processing method=%s url=%s session_id=%s",
                request.method,
                str(request.url),
                session_id,
            )
            raise
        finally:
            duration_ms = (time.perf_counter() - start) * 1000
            status_code = response.status_code if response is not None else 500
            logger.info(
                "request method=%s url=%s status=%s duration_ms=%.2f session_id=%s",
                request.method,
                str(request.url),
                status_code,
                duration_ms,
                session_id,
            )

        if response is None:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=error_payload(
                    error_code="internal_error",
                    message="Internal server error",
                    details={"path": request.url.path},
                ),
            )

        if SESSION_COOKIE_NAME not in request.cookies:
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
