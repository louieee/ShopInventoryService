from typing import Any

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
	first_name: str
	last_name: str
	email: EmailStr


class CreateUser(UserBase):
	password: str

	def validate_data(self) -> Any:
		initial_data = self.dict()
		if not any(char.isdigit() for char in initial_data['password']):
			raise ValueError("Password must contain at least one digit")
		return CreateUser(**initial_data)


class User(UserBase):
	id: int

	class Config:
		from_attributes = True
		orm_mode = True


class LoginSchema(BaseModel):
	email: EmailStr
	password: str
