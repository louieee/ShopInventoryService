import dataclasses
from typing import Optional


@dataclasses.dataclass
class UserPayload:
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

