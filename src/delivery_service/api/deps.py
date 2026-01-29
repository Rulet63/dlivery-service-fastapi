from __future__ import annotations

from typing import cast

from fastapi import HTTPException, Request, status


def get_session_id(request: Request) -> str:
    session_id_any = getattr(request.state, "session_id", None)

    if not session_id_any:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": "session_not_initialized",
                "message": "session_id is not set in request.state",
            },
        )

    return cast(str, session_id_any)
