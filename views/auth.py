from typing import List

from django.http import JsonResponse
from fastapi import APIRouter, UploadFile, Header
from fastapi import HTTPException, Depends
from pydantic import ValidationError
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

import crud
import schemas
import tasks
from helpers.response import FailureResponse, SuccessResponse
from helpers.utilities import send_ws_single_channel
from settings.database import get_db
from settings.jwt_config import create_access_token, get_current_user, create_refresh_token, refresh_access_token

router = APIRouter(prefix="/auth", tags=['auth'])


@router.post("/login")
async def login_for_access_token(credentials: schemas.LoginSchema, db: Session = Depends(get_db)):
	user = crud.get_user_by_email(db, credentials.email)
	if not user:
		return FailureResponse(message="You dont have an account with us")
	if not user.check_password(credentials.password):
		return FailureResponse(message="Incorrect credentials")
	user = schemas.User.model_validate(user)
	data = {"access_token": create_access_token(user),
	        "refresh_token": create_refresh_token(user),
	        "token_type": "bearer"}
	send_ws_single_channel(user, "general", "Logged In", user.dict())
	tasks.just_comment.delay()
	return SuccessResponse(message="Login is successful", data=data)


@router.post("/refresh-access-token/", response_model=schemas.User)
async def request_access_token(refresh_token: str = Header(title="refresh_token")):
	access_token = refresh_access_token(refresh_token)
	return JSONResponse(dict(access_token=access_token))


@router.post("/signup/", response_model=schemas.User)
async def signup(data: schemas.CreateUser,
                 db: Session = Depends(get_db)):
	try:
		data = data.validate_data()
	except ValueError as e:
		return FailureResponse(message=e.__str__())
	if crud.get_user_by_email(db, email=data.email, exists=True):
		return FailureResponse(message="A user with this email already exists")
	await crud.create_user(db=db, user=data)
	return SuccessResponse(message="Signup is successful")
