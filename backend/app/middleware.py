import uuid
from contextvars import ContextVar

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# Context variable for request ID
request_id_context: ContextVar[str] = ContextVar("request_id", default="")

# Middleware to manage request IDs
class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Check if request ID exists in headers, otherwise generate a new one
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request_id_context.set(request_id)
        request.state.request_id = request_id

        # Proceed with the request and set the ID in the response headers
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response