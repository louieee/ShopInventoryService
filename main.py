from fastapi import FastAPI, Depends
from fastapi.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

import consumer
import settings
from views import auth, profile, user
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
	Middleware(LoggingMiddleware)

]

create_db()
app = FastAPI(middleware=middlewares)


@app.get("/sentry-debug")
async def trigger_error():
	division_by_zero = 1 / 0


app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(user.router)
app.include_router(consumer.router)
