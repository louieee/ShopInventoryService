from typing import List

from fastapi import APIRouter
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session

import crud
import schemas
from helpers.response import pagination_params
from settings.database import get_db
from settings.jwt_config import get_current_user

router = APIRouter(prefix="/users", tags=['users'])


@router.get("/", response_model=List[schemas.User])
async def read_users(db: Session = Depends(get_db),
                     current_user: dict = Depends(get_current_user),
                     pagination: dict = Depends(pagination_params)
                     ):
	page = pagination['page']
	per_page = pagination['per_page']
	db_user = crud.get_users(db, ((page - 1) * per_page), per_page)
	if db_user is None:
		raise HTTPException(status_code=404, detail="User not found")
	return db_user


@router.get("/{user_id}", response_model=schemas.User)
async def read_users(user_id: int, db: Session = Depends(get_db),
                     current_user: dict = Depends(get_current_user),
                     ):
	db_user = crud.get_user(db, user_id=user_id)
	if db_user is None:
		raise HTTPException(status_code=404, detail="User not found")
	return db_user
