from fastapi import UploadFile
from sqlalchemy import text

import models
from helpers.exceptions import ValidationError
from .helpers import *
from schemas import products as schemas


class ProductRepository(BaseRepository):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.model = models.Product

	@staticmethod
	def query_parameters(brands: list[int] = Query(default=None, title="brands", description="filter by brands"),
	                     inventories: list[int] = Query(default=None, title="inventory",
	                                                          description="filter by inventories"),
	                     search: str = Query(default=None, title="search", description="search for inventories"),
	                     start_price: float = Query(default=None, title="start_price",
	                                                       description=" start price range"),
	                     end_price: float = Query(default=None, title="end_price",
	                                                     description="end price range")
	                     ):
		return {"brands": brands, "inventories": inventories,
		        "search": search, "start_price": start_price,
		        "end_price": end_price}

	async def get_all(self, skip: int = 0, limit: int = 100,
	                  brands: List[int] = None,
	                  inventories: List[int] = None,
	                  search: str = None,
	                  start_price: float = None,
	                  end_price: float = None):
		querystring = "select * from products_view"
		params = dict()

		if brands:
			querystring = f"{querystring} where brand_id in :brand_ids"
			params["brand_ids"] = tuple(brands)
		if inventories:
			querystring = f"{querystring} {'where' if 'where' not in querystring else 'and'} inventory_id in :inventory_ids"
			params["inventory_ids"] = tuple(inventories)
		if search:
			querystring = f"{querystring} {'where' if 'where' not in querystring else 'and'} description ilike :search or name ilike :search"
			params["search"] = f"%{search}%"
		if start_price and not end_price:
			querystring = f"{querystring} {'where' if 'where' not in querystring else 'and'} price >= :start_price"
			params["start_price"] = start_price
		elif not start_price and end_price:
			querystring = f"{querystring} {'where' if 'where' not in querystring else 'and'} price <= :end_price"
			params["end_price"] = end_price
		elif start_price and end_price:
			querystring = f"{querystring} {'where' if 'where' not in querystring else 'and'} price >= :start_price and price <= :end_price"
			params["start_price"] = start_price
			params["end_price"] = end_price
		count = self.db.execute(text(querystring.replace("select *", "select count(*)", 1)),
		                        params).mappings().first()["count"]
		querystring = f"{querystring} order by name limit :limit offset :offset;"
		params["limit"] = limit
		params["offset"] = skip
		querystring = text(querystring)
		return dict(results=self.db.execute(querystring, params).mappings().all(), count=count)

	@exception_quieter
	async def get_by_id(self, id: int, exists=False):
		product = await self.get(id=id, exists=exists)
		if not product:
			raise NotFoundError("This product does not exist")
		return product

	async def get_by_name(self, name:str, brand_id:int=None, inventory_id:int=None, exclude_id:int=None, exists=False):
		params = dict(name=f"%{name}%")
		if exists:
			querystring = "select id from products_view where name ilike :name"
		else:
			querystring = "select * from products_view where name ilike :name"
		if brand_id:
			querystring = f"{querystring} and brand_id = :brand_id"
			params["brand_id"] = brand_id
		if inventory_id:
			querystring = f"{querystring} and inventory_id = :inventory_id"
			params["inventory_id"] = inventory_id
		if exclude_id:
			querystring = f"{querystring} and id != :exclude_id"
			params["exclude_id"] = exclude_id
		querystring = text(f"{querystring};")
		result = self.db.execute(querystring, params).mappings().all()
		if exists:
			return len(result) > 0
		return result[0] if result else None


	@exception_quieter
	async def create(self, item: schemas.CreateProduct, **kwargs):
		product_exist = await self.get_by_name(name=item.name,
		                                       inventory_id=item.inventory_id,
		                                       brand_id=item.brand_id,
		                                       exists=True)
		if product_exist:
			raise ValidationError(detail="This product already exists")

		images: List[UploadFile] = kwargs.pop("images", list())
		product: models.Product = await super(ProductRepository, self).create(item, **kwargs)
		for image in images:
			models.ProductFile.save(name=image.file.name,
			                        content=image.file.read(),
			                        product_id=product.id)

		return product

	@exception_quieter
	async def add_images(self, id, images: List[UploadFile]):

		product_exist = await self.get_by_id(id=id, exists=True)
		if not product_exist:
			raise NotFoundError(detail="This product does not exist")

		product_files = [models.ProductFile.save(name=image.filename,
			                                       content=await image.read(),
			                                       product_id=id)
		for image in images]
		self.db.bulk_save_objects(product_files)
		self.db.commit()
		return await self.get_by_id(id=id)


	@exception_quieter
	async def delete_images(self, id, image_ids: List[int]):
		product_exist = await self.get_by_id(id=id, exists=True)
		if not product_exist:
			raise ValidationError(detail="This product does not exist")

		query = self.db.query(models.ProductFile).filter(models.ProductFile.id.in_(image_ids),
                        models.ProductFile.product_id.in_([id]))
		for img in query:
			await pre_delete.send(img)
		query.delete(synchronize_session=False)
		self.db.commit()
		return await self.get_by_id(id=id)

	@exception_quieter
	async def update(self, id: int, new_data: schemas.CreateProduct):
		product_exist = await self.get_by_id(id=id, exists=True)
		if not product_exist:
			raise NotFoundError(detail="This product does not exist")

		details_exist = await self.get_by_name(name=new_data.name, inventory_id=new_data.inventory_id,
		                                       brand_id=new_data.brand_id, exclude_id=id,
		                                       exists=True)
		if details_exist:
			raise ValidationError(detail="A product with this name already exists")
		return await super().update(id=id, new_data=new_data)

class ProductFileRepository(BaseRepository):
	model = models.ProductFile

