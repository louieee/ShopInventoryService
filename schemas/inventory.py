from datetime import datetime
from typing import Any, List

from pydantic import BaseModel


class InventoryBase(BaseModel):
	name: str
	description: str
	date_of_acquisition: datetime
	location: str


class CreateInventory(InventoryBase):

	def validate_data(self) -> Any:
		initial_data = self.dict()
		if not any(char.isdigit() for char in initial_data['password']):
			raise ValueError("Password must contain at least one digit")
		return CreateInventory(**initial_data)


class Inventory(InventoryBase):
	id: int

	class Config:
		from_attributes = True
		orm_mode = True

class InventoryListResponse(BaseModel):
	count: int
	result: List[Inventory]


