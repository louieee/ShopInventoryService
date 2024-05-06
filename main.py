from fastapi import FastAPI
from fastapi.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

import consumer
import settings
from views import products, inventory, brands, sales
from settings.celery_config import celery  # noqa
from settings.database import create_db
from middlewares import LoggingMiddleware
import sentry_sdk

sentry_sdk.init(
	dsn="",
	enable_tracing=True,
)


middlewares = [
	Middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS),
	Middleware(CORSMiddleware, allow_origins=settings.CORS_ORIGINS, allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
	           allow_methods=settings.CORS_ALLOW_METHODS, allow_headers=settings.CORS_ALLOW_HEADERS),
	Middleware(LoggingMiddleware),

]

create_db()
app = FastAPI(middleware=middlewares)

@app.get("/sentry-debug")
async def trigger_error():
	division_by_zero = 1 / 0

app.include_router(brands.router)
app.include_router(products.router)
app.include_router(inventory.router)
app.include_router(consumer.router)
app.include_router(sales.router)
