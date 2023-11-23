
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class LoggingMiddleware(BaseHTTPMiddleware):
	async def dispatch(self, request: Request, call_next):
		start_time = time.time()
		response = await call_next(request)
		if response.status_code >= 500:
			response.status_code = 400
		process_time = time.time() - start_time
		response.headers["X-Process-Time"] = str(process_time)
		return response
