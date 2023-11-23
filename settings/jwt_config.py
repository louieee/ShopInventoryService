# main.py
from datetime import datetime, timedelta
from typing import Any, Union

from decouple import config
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from starlette.requests import Request

import settings
from schemas import User
from settings import SECRET_KEY

# JWT Configuration
ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.JWT_ACCESS_TOKEN_EXPIRY# 30 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = settings.JWT_REFRESH_TOKEN_EXPIRY
JWT_SECRET = settings.JWT_SECRET_KEY


# Function to create JWT token

def create_access_token(user: User, expires_delta: int = None) -> str:
	if expires_delta is not None:
		expires_delta = datetime.utcnow() + timedelta(minutes=expires_delta)
	else:
		expires_delta = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

	to_encode = {"exp": expires_delta, "user": user.dict()}
	encoded_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)
	return encoded_jwt


def create_refresh_token(user: User, expires_delta: int = None) -> str:
	if expires_delta is not None:
		expires_delta = datetime.utcnow() + timedelta(minutes=expires_delta)
	else:
		expires_delta = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

	to_encode = {"exp": expires_delta, "user": user.dict()}
	encoded_jwt = jwt.encode(to_encode, JWT_SECRET, ALGORITHM)
	return encoded_jwt


# Function to decode JWT token
def decode_access_token(token: str):
	error = dict(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail="Could not validate credentials",
		headers={"WWW-Authenticate": "Bearer"})
	try:
		payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

		if datetime.utcnow().__ge__(datetime.fromtimestamp(payload['exp'])):
			error['detail'] = "Expired access token"
			raise HTTPException(**error)
		return payload['user']
	except JWTError:
		raise HTTPException(**error)


def validate_refresh_token(token: str):
	error = dict(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail="Could not validate credentials",
		headers={"WWW-Authenticate": "Bearer"})
	try:
		payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
		if datetime.utcnow().__ge__(datetime.fromtimestamp(payload['exp'])):
			error['detail'] = "Expired refresh token"
			raise HTTPException(**error)
		return payload['user']
	except JWTError:
		raise HTTPException(**error)


def refresh_access_token(refresh_token: str):
	user = validate_refresh_token(refresh_token)
	return create_access_token(User(**user))


class JWTBearer(HTTPBearer):
	def __init__(self, auto_error: bool = True):
		super(JWTBearer, self).__init__(auto_error=auto_error)

	async def __call__(self, request: Request):
		credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
		if credentials:
			if not credentials.scheme == "Bearer":
				raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
			if not self.verify_jwt(credentials.credentials):
				raise HTTPException(status_code=403, detail="Invalid token or expired token.")
			return credentials.credentials
		else:
			raise HTTPException(status_code=403, detail="Invalid authorization code.")

	def verify_jwt(self, jwtoken: str) -> bool:
		isTokenValid: bool = False
		payload = decode_access_token(jwtoken)
		if payload:
			isTokenValid = True
		return isTokenValid


oauth2_scheme = JWTBearer()


def get_current_user(token: str = Depends(oauth2_scheme)):
	payload = decode_access_token(token)
	return payload
