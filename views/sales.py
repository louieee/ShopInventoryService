from typing import List

from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from schemas.helpers import SuccessResponse
import schemas.sales as schemas
from helpers.response import pagination_params
from repositories import sales as repository
from settings.database import get_db
from settings.jwt_config import get_current_user

router = APIRouter(prefix="/sales", tags=['sales'])


@router.get("/" , response_model=schemas.SaleListResponse)
async def fetch_sales(db: Session = Depends(get_db),
                         current_user: dict = Depends(get_current_user),
                         pagination: dict = Depends(pagination_params),
                         query: dict = Depends(repository.SaleRepository.query_parameters)
                         ):
	page = pagination['page']
	per_page = pagination['per_page']
	repo = repository.SaleRepository(db, current_user)
	products = await repo.get_all(skip=((page - 1) * per_page),
	                              limit=per_page, **query)
	return products



@router.get("/{sale_id}", response_model=schemas.SalesDetailResponse)
async def get_sale_details(sale_id: int, db: Session = Depends(get_db),
                       current_user: dict = Depends(get_current_user),
                       ):
	repo = repository.SaleRepository(db, current_user)
	return await repo.get_by_id(sale_id)

@router.post("/", response_model=SuccessResponse)
async def create_sale(data: schemas.CreateSale,
                         db: Session = Depends(get_db),
                         current_user: dict = Depends(get_current_user),

                         ):
	repo = repository.SaleRepository(db, current_user)
	return await repo.create(data)


@router.delete("/{sale_id}", responses={204: {"model": None}})
async def delete_sale(sale_id: int, db: Session = Depends(get_db),
                         current_user: dict = Depends(get_current_user),
                         ):
	repo = repository.SaleRepository(db, current_user)
	return await repo.delete(id=sale_id)


@router.post("/{sale_id}/orders", response_model=SuccessResponse)
async def add_orders(sale_id:int, data: List[schemas.OrderItem], db:Session = Depends(get_db),
                    current_user: dict=Depends(get_current_user)
                     ):
	repo = repository.SaleRepository(db, current_user)
	return await repo.add_orders(id=sale_id, orders=data)


@router.delete("/{sale_id}/orders", response_model=SuccessResponse)
async def remove_orders(sale_id:int, data: List[int], db:Session=Depends(get_db),
                        current_user: dict=Depends(get_current_user)
                        ):
	repo = repository.SaleRepository(db, current_user)
	return await repo.remove_orders(id=sale_id, order_ids=data)


@router.patch("/{sale_id}", response_model=SuccessResponse)
async def mark_sale_paid(sale_id:int, db:Session=Depends(get_db),
                        current_user: dict=Depends(get_current_user)
                         ):
	repo = repository.SaleRepository(db, current_user)
	return await repo.mark_paid(id=sale_id)


@router.post("/staff/{staff_id}/orders", response_model=SuccessResponse)
async def assign_staff_to_orders(staff_id:int, data: List[int],
                                 db:Session=Depends(get_db),
                        current_user: dict=Depends(get_current_user)
                                 ):
	repo = repository.SaleRepository(db, current_user)
	return await repo.assign_staff_to_orders(staff_id=staff_id, order_ids=data)

@router.delete("/staff/{staff_id}/orders", response_model=SuccessResponse)
async def remove_staff_to_orders(staff_id:int, data:List[int],
                                 db:Session=Depends(get_db),
                        current_user: dict=Depends(get_current_user)
                                 ):
	repo = repository.SaleRepository(db, current_user)
	return await repo.remove_staff_from_orders(staff_id=staff_id, order_ids=data)


@router.patch("/orders/{order_id}", response_model=SuccessResponse)
async def mark_order_as_delivered(order_id:int,
                                 db:Session=Depends(get_db),
                        current_user: dict=Depends(get_current_user)
                                  ):
	repo = repository.SaleRepository(db, current_user)
	return await repo.mark_order_as_delivered(order_id=order_id)