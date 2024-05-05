from typing import List

from fastapi import APIRouter, UploadFile
from fastapi import HTTPException, Depends, Query
from sqlalchemy.orm import Session

import models
import schemas.brands as schemas
from helpers.response import pagination_params, SuccessResponse, FailureResponse, exception_quieter
from settings.database import get_db
from settings.jwt_config import get_current_user
from repositories import brands as repository

router = APIRouter(prefix="/brands", tags=['brand'])


@router.get("/", response_model=schemas.BrandListResponse)
async def fetch_brands(db: Session = Depends(get_db),
                       current_user: dict = Depends(get_current_user),
                       pagination: dict = Depends(pagination_params),
                       query: dict = Depends(repository.BrandRepository.query_parameters)
                       ):
	page = pagination['page']
	per_page = pagination['per_page']
	repo = repository.BrandRepository(db, current_user)
	return await repo.get_all(skip=((page - 1) * per_page), limit=per_page, **query)


@router.get("/{brand_id}", response_model=schemas.Brand)
async def read_brand(brand_id: int, db: Session = Depends(get_db),
                     current_user: dict = Depends(get_current_user),
                     ):
	repo = repository.BrandRepository(db, current_user)
	brand = await repo.get(brand_id)
	if brand is None:
		return FailureResponse(status=404, message="Brand not found")
	return brand


@router.post("/", response_model=schemas.Brand)
async def create_brand(data: schemas.CreateBrand,
                       db: Session = Depends(get_db),
                       current_user: dict = Depends(get_current_user),

                       ):
	repo = repository.BrandRepository(db, current_user)
	return await repo.create(data)


@router.put("/{brand_id}", response_model=schemas.Brand)
async def update_brand(data: schemas.CreateBrand, brand_id: int, db: Session = Depends(get_db),
                       # current_user: dict = Depends(get_current_user),
                       ):
	repo = repository.BrandRepository(db)
	return await repo.update(id=brand_id, new_data=data)


@router.delete("/{brand_id}", response_model=schemas.Brand)
async def delete_brand(brand_id: int, db: Session = Depends(get_db),
                       current_user: dict = Depends(get_current_user),
                       query: dict = Depends(repository.BrandRepository.delete_parameters)
                       ):
	repo = repository.BrandRepository(db, current_user)
	return await repo.delete(id=brand_id, **query)
