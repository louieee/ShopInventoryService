from typing import List

from fastapi import APIRouter
from fastapi import HTTPException, Depends, Query
from sqlalchemy.orm import Session

import models
import schemas.inventory as schemas
from helpers.response import pagination_params, SuccessResponse, FailureResponse, exception_quieter
from settings.database import get_db
from settings.jwt_config import get_current_user
from repositories import inventory as repository

router = APIRouter(prefix="/inventories", tags=['inventory'])


@router.get("/", response_model=schemas.InventoryListResponse)
async def fetch_inventories(db: Session = Depends(get_db),
                            current_user: dict = Depends(get_current_user),
                            pagination: dict = Depends(pagination_params),
                            query: dict = Depends(repository.InventoryRepository.query_parameters)
                            ):
	page = pagination['page']
	per_page = pagination['per_page']
	repo = repository.InventoryRepository(db, current_user)
	inventories = await repo.get_all(skip=((page - 1) * per_page),
	                                 limit=per_page, **query)
	return inventories


@router.get("/{inventory_id}", response_model=schemas.Inventory)
async def read_inventory(inventory_id: int, db: Session = Depends(get_db),
                         current_user: dict = Depends(get_current_user),
                         ):
	repo = repository.InventoryRepository(db, current_user)
	inventory = await repo.get(inventory_id)
	if inventory is None:
		return FailureResponse(status=404, message="Inventory not found")
	return inventory


@router.post("/", response_model=schemas.Inventory)
async def create_inventory(data: schemas.CreateInventory,
                           db: Session = Depends(get_db),
                           current_user: dict = Depends(get_current_user),

                           ):
	repo = repository.InventoryRepository(db, current_user)
	return await repo.create(data)

@router.put("/{inventory_id}", response_model=schemas.Inventory)
async def update_inventory(data: schemas.CreateInventory, inventory_id: int, db: Session = Depends(get_db),
                           current_user: dict = Depends(get_current_user),
                           ):
	repo = repository.InventoryRepository(db, current_user)
	inventory: models.Inventory = await repo.update(id=inventory_id, new_data=data)
	return inventory


@router.delete("/{inventory_id}")
async def delete_inventory(inventory_id: int, db: Session = Depends(get_db),
                           current_user: dict = Depends(get_current_user),
                           query: dict = Depends(repository.InventoryRepository.delete_parameters)
                           ):
	repo = repository.InventoryRepository(db, current_user)
	return await repo.delete(id=inventory_id, **query)
