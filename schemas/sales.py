from datetime import datetime
from typing import List

from pydantic import BaseModel


class OrderItem(BaseModel):
	product_id: int
	quantity: int

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
	date_ordered: datetime
	date_paid: datetime
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
	delivered: bool
	staff_id: int
	staff: str # staff's name



class SalesDetailResponse(SaleListItem):
	orders = List[OrderListItem]
	location: str







