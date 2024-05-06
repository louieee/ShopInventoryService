from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class OrderItem(BaseModel):
	product_id: int
	quantity: int = Field(gt=0)

class CreateSale(BaseModel):
	orders: List[OrderItem]
	customer_id: int
	location: str



class AssignStaffToOrders(BaseModel):
	staff_id: int
	order_ids: List[int]


class SaleListItem(BaseModel):
	id: int
	paid: bool
	date_ordered: Optional[datetime]
	date_paid: Optional[datetime]
	customer_id: int
	customer: str  # customer name
	orders_count: int
	total_amount: float

class SaleListResponse(BaseModel):
	count: int
	results: List[SaleListItem]


class OrderListItem(OrderItem):
	id: int
	product: str # product's name
	price:float
	total_price: float
	delivered: bool
	staff_id: Optional[int]
	staff: Optional[str] # staff's name



class SalesDetailResponse(SaleListItem):
	orders: List[OrderListItem]
	location: str







