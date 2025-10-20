import time
from typing import Callable

from fastapi import Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware


class LoggingMiddleware(BaseHTTPMiddleware):
    """Enhanced logging middleware with request/response details."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )

        response = await call_next(request)

        process_time = time.time() - start_time
        logger.info(f"Response: {response.status_code} in {process_time:.4f}s")

        return response
