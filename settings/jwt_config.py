# main.py
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from starlette.requests import Request

import settings
from schemas.inventory import Inventory
from schemas.users import UserBase, UserType

# JWT Configuration
ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.JWT_ACCESS_TOKEN_EXPIRY# 30 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = settings.JWT_REFRESH_TOKEN_EXPIRY
JWT_SECRET = settings.JWT_SECRET_KEY
JWT_ISSUER = settings.JWT_ISSUER


# Function to create JWT token

def convert_payload_to_base_model(payload:dict):
	user_type = payload.pop("user_type", None)
	payload["staff_id"] = None
	payload["customer_id"] = None
	payload["admin_id"] = None

	if user_type == UserType.ADMINISTRATOR:
		payload["admin_id"] = payload["id"]
		payload["id"] = payload.pop("user_id")
	elif user_type == UserType.STAFF:
		payload["staff_id"] = payload["id"]
		payload["id"] = payload.pop("user_id")
	elif payload["user_type"] == UserType.CUSTOMER:
		payload["customer_id"] = payload["id"]
		payload["id"] = payload.pop("user_id")
	else:
		raise HTTPException(detail="Invalid user type", status_code=400)
	return UserBase(**payload)

def create_access_token(user: UserBase, expires_delta: int = None) -> str:
	if expires_delta is not None:
		expires_delta = datetime.utcnow() + timedelta(minutes=expires_delta)
	else:
		expires_delta = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

	to_encode = {"exp": expires_delta, "user": user.model_dump(), "iss": JWT_ISSUER}
	encoded_jwt = jwt.encode(to_encode, JWT_SECRET, ALGORITHM)
	return encoded_jwt


def create_refresh_token(user: Inventory, expires_delta: int = None) -> str:
	if expires_delta is not None:
		expires_delta = datetime.utcnow() + timedelta(minutes=expires_delta)
	else:
		expires_delta = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

	to_encode = {"exp": expires_delta, "user": user.dict(), "iss":JWT_ISSUER}
	encoded_jwt = jwt.encode(to_encode, JWT_SECRET, ALGORITHM)
	return encoded_jwt


# Function to decode JWT token
def decode_access_token(token: str):
	error = dict(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail="Could not validate credentials",
		headers={"WWW-Authenticate": "Bearer"})
	try:
		payload = jwt.decode(token, JWT_SECRET, algorithms=ALGORITHM, issuer=JWT_ISSUER)
		if datetime.utcnow().__ge__(datetime.fromtimestamp(payload['exp'])):
			error['detail'] = "Expired access token"
			raise HTTPException(**error)
		return convert_payload_to_base_model(payload['user'])
	except JWTError as e:
		print(e)
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
		return convert_payload_to_base_model(payload['user'])
	except JWTError:
		raise HTTPException(**error)


def refresh_access_token(refresh_token: str):
	user = validate_refresh_token(refresh_token)
	return create_access_token(user)


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

	@staticmethod
	def verify_jwt(token: str) -> bool:
		is_token_valid: bool = False
		payload = decode_access_token(token)
		if payload:
			is_token_valid = True
		return is_token_valid


oauth2_scheme = JWTBearer()


def get_current_user(token: str = Depends(oauth2_scheme)):
	payload = decode_access_token(token)
	return payload