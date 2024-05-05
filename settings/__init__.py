import os.path

from decouple import config

# Dependency

APP_NAME = "AccountService"

SECRET_KEY = config("SECRET_KEY")
ALLOWED_HOSTS = ["localhost"]

DATABASE_URL = config("DATABASE_URL")

CORS_ORIGINS = [
	"http://localhost.tiangolo.com",
	"https://localhost.tiangolo.com",
	"http://localhost",
	"http://localhost:8080",
]
CORS_ALLOW_METHODS = ["*"]
CORS_ALLOW_HEADERS = ["*"]
CORS_ALLOW_CREDENTIALS = True

JWT_SECRET_KEY = config("JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRY = 60 * 24 * 1
JWT_REFRESH_TOKEN_EXPIRY = 60 * 24 * 3
JWT_ISSUER = "sales-app"

CELERY_BROKER = "redis://localhost:6379/0"
CELERY_BACKEND = "redis://localhost:6379/0"
CELERY_RESULT_EXPIRY = 3600
CELERY_TIMEZONE = "UTC"

BASE_PATH = os.path.abspath("").split('/')
BASE_URL = "/".join(BASE_PATH)
MEDIA_PATH = "media"
MEDIA_URL = os.path.join(BASE_URL, MEDIA_PATH)

AWS_S3_BUCKET_NAME = ""
AWS_SECRET_KEY = ""
AWS_ACCESS_KEY = ""

UPLOAD_TYPE = "file"
