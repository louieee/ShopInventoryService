from fastapi import APIRouter
from fastapi import Depends

import schemas
from settings.jwt_config import get_current_user

router = APIRouter(prefix="/user/me", tags=["profile"])


@router.get("/", response_model=schemas.User)
async def read_user(current_user: dict = Depends(get_current_user)):
	return current_user
