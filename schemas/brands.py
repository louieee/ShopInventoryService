from typing import List

from pydantic import BaseModel
from pydantic.v1 import Field


class BrandBase(BaseModel):
	name: str = Field(min_items=10)
	description: str


class CreateBrand(BrandBase):
	...


class Brand(BrandBase):
	id: int

	class Config:
		from_attributes = True
		orm_mode = True


class BrandListResponse(BaseModel):
	count: int
	results: List[Brand]


