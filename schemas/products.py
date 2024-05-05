from typing import List

from pydantic import BaseModel

from schemas.brands import Brand
from schemas.inventory import Inventory


class ProductImageBase(BaseModel):
	name: str
	url: str


class ProductImage(ProductImageBase):
	id: int

	class Config:
		from_attributes = True
		orm_mode = True


class ProductBase(BaseModel):
	name: str
	description: str
	brand_id: int
	inventory_id: int
	price: float
	quantity: int


class CreateProduct(ProductBase):
	...

class CreateProductResponse(ProductBase):
	id: int

class ProductDetailResponse(BaseModel):
	id: int
	name: str
	description: str
	brand: Brand
	inventory: Inventory
	price: float
	quantity: int
	images : List[ProductImage]


class ProductResponse(ProductBase):
	id: int
	brand: str
	inventory: str
	images: List[str]

class ProductListResponse(BaseModel):
	count: int
	results: List[ProductResponse]


