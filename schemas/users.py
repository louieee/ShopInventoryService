from typing import Optional

from pydantic import BaseModel

class UserType:
	CUSTOMER = "Customer"
	ADMINISTRATOR = "Administrator"
	STAFF = "Staff"

class UserBase(BaseModel):
	id: int
	first_name: str
	last_name: str
	email: str
	customer_id : Optional[int]
	staff_id: Optional[int]
	admin_id: Optional[int]

