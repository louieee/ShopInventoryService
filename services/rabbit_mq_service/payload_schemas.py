import dataclasses
from abc import ABC
from datetime import datetime
from typing import Optional, Literal


@dataclasses.dataclass
class BasePayload(ABC):
	def as_dict(self):
		return dataclasses.asdict(self)


@dataclasses.dataclass
class RabbitMQPayload(BasePayload):
	action: Literal["create", "update", "delete"]
	data_type : str
	data: str

@dataclasses.dataclass
class UserPayload(BasePayload):
	id: int
	first_name: str
	last_name: str
	email: str
	is_customer: bool
	is_admin: bool
	is_staff: bool
	display_name: str
	profile_pic: str
	gender: str
	date_of_birth: str
	customer_id: Optional[int] = dataclasses.field(default=None)
	staff_id: Optional[int] = dataclasses.field(default=None)
	admin_id: Optional[int] = dataclasses.field(default=None)

@dataclasses.dataclass
class OrderPayload(BasePayload):
	id: int
	product_id: int
	sale_id: int
	staff_id: int
	quantity: int
	delivered: bool
	total_amount: float
	date_delivered: Optional[datetime] = dataclasses.field(default=None)

@dataclasses.dataclass
class ProductPayload(BasePayload):
	id: int
	name: str
	brand: str
	inventory: str
	price: float
	quantity: int
	description: str
	category: str

@dataclasses.dataclass
class SalePayload(BasePayload):
	id: int
	paid: bool
	customer_id: int
	location: str
	date_ordered: datetime
	date_paid: Optional[datetime] = dataclasses.field(default=None)


