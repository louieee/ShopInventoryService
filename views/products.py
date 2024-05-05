from typing import List

from fastapi import APIRouter, UploadFile, Form
from fastapi import HTTPException, Depends, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

import models
import schemas.products as schemas
from helpers.response import pagination_params, SuccessResponse, FailureResponse
from settings.database import get_db
from repositories import products as repository
from settings.jwt_config import get_current_user

router = APIRouter(prefix="/products", tags=['product'])


@router.get("/" , response_model=schemas.ProductListResponse)
async def fetch_products(db: Session = Depends(get_db),
                         current_user: dict = Depends(get_current_user),
                         pagination: dict = Depends(pagination_params),
                         query: dict = Depends(repository.ProductRepository.query_parameters)
                         ):
	page = pagination['page']
	per_page = pagination['per_page']
	repo = repository.ProductRepository(db, current_user)
	products = await repo.get_all(skip=((page - 1) * per_page),
	                              limit=per_page, **query)
	return products



@router.get("/{product_id}", response_model=schemas.ProductDetailResponse)
async def read_product(product_id: int, db: Session = Depends(get_db),
                       current_user: dict = Depends(get_current_user),
                       ):
	repo = repository.ProductRepository(db, current_user)
	product = await repo.get_by_id(product_id)
	if product is None:
		return FailureResponse(status=404, message="Product not found")
	return product


@router.post("/", response_model=schemas.CreateProductResponse)
async def create_product(data: schemas.CreateProduct,
                         db: Session = Depends(get_db),
                         current_user: dict = Depends(get_current_user),

                         ):
	repo = repository.ProductRepository(db, current_user)
	product_exist = await repo.get_by_name(name=data.name,
	                                 inventory_id=data.inventory_id,
	                                 brand_id=data.brand_id,
	                                 exists=True)
	if product_exist:
		return FailureResponse(message="This product already exists")
	product: models.Product = await repo.create(data)
	return product

@router.post("/{product_id}/images", response_model=schemas.ProductDetailResponse)
async def add_product_images(product_id: int, images: List[UploadFile],
                             db:Session=Depends(get_db),
current_user: dict = Depends(get_current_user),
                             ):
	repo = repository.ProductRepository(db, current_user)
	product_exist = await repo.get_by_id(id=product_id, exists=True)
	if not product_exist:
		return FailureResponse(message="Product not found", status=404)

	product = await repo.add_images(id=product_id, images=images)
	return product

@router.delete("/{product_id}/images", response_model=schemas.ProductDetailResponse)
async def delete_product_images(product_id: int, images: List[int], db:Session=Depends(get_db),
                                current_user: dict = Depends(get_current_user),):
	repo = repository.ProductRepository(db, current_user)
	product_exist = await repo.get_by_id(id=product_id, exists=True)
	if not product_exist:
		return FailureResponse(message="Product not found", status=404)

	product = await repo.delete_images(id=product_id, image_ids=images)
	return product
@router.put("/{product_id}", response_model=schemas.CreateProductResponse)
async def update_product(data: schemas.CreateProduct, product_id: int, db: Session = Depends(get_db),
                         current_user: dict = Depends(get_current_user),
                         ):
	repo = repository.ProductRepository(db, current_user)
	product_exist = await repo.get_by_id(id=product_id, exists=True)
	if not product_exist:
		return FailureResponse(message="Product not found", status=404)


	details_exist = await repo.get_by_name(name=data.name, inventory_id=data.inventory_id,
	                                 brand_id=data.brand_id, exclude_id=product_id,
	                                 exists=True)
	if details_exist:
		return FailureResponse(message="A product with this name already exists")
	product: models.Product = await repo.update(id=product_id, new_data=data)
	return product


@router.delete("/{product_id}", response_model=schemas.ProductResponse)
async def delete_product(product_id: int, db: Session = Depends(get_db),
                         current_user: dict = Depends(get_current_user),
                         ):
	repo = repository.ProductRepository(db, current_user)
	return await repo.delete(id=product_id)
