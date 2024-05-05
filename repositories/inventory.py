from datetime import datetime

from sqlalchemy import or_

import models
from helpers.exceptions import ValidationError
from .helpers import *
from .products import ProductRepository


class InventoryRepository(BaseRepository):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.model = models.Inventory

	@exception_quieter
	async def create(self, item: BaseModel, **kwargs):
		# check if db has an inventory with that name
		query = self.db.query(self.model).filter(self.model.name == str(item.name).title())
		exists = query.count() > 0
		if exists:
			raise ValidationError(detail="An inventory with this name already exists")
		return await super(InventoryRepository, self).create(item)

	@staticmethod
	def query_parameters(location: str = Query(default=None, title="location", description="filter by location"),
	                     search: str = Query(default=None, title="search", description="search for inventories"),
	                     start_date: datetime = Query(default=None, title="start_date",
	                                                         description="date of acquisition start date range"),
	                     end_date: datetime = Query(default=None, title="end_date",
	                                                       description="date of acquisition end date range")
	                     ):
		return {"location": location, "search": search, "start_date": start_date,
		        "end_date": end_date}

	async def get_all(self, skip: int = 0, limit: int = 100,
	                  location: str = None, search: str = None,
	                  start_date: datetime = None,
	                  end_date: datetime = None):
		queryset = await self.get_queryset()
		if location:
			queryset = await self.get_queryset(queryset=queryset, location=location)
		if search:
			queryset = queryset.filter(or_(self.model.name.icontains(search),
			                               self.model.location.icontains(search),
			                               self.model.description.icontains(search)))
		if start_date and not end_date:
			queryset = queryset.filter(self.model.date_of_acquisition.__ge__(start_date))
		elif not start_date and end_date:
			queryset = queryset.filter(self.model.date_of_acquisition.__le__(end_date))
		elif start_date and end_date:
			queryset = queryset.filter(self.model.date_of_acquisition.between(start_date, end_date))
		return {"result": queryset.offset(skip).limit(limit).all(), "count": queryset.count()}

	@exception_quieter
	async def delete(self, id: int, **kwargs):
		force: bool = kwargs.pop("force", False)
		if force is False :
			products = await ProductRepository(db=self.db, user=self.user).get_queryset(inventory_id=id)
			if products.count() > 0:
				raise ValidationError(detail="This inventory still has products in it and therefore cannot be deleted")
		return await super(InventoryRepository, self).delete(id)

	@exception_quieter
	async def update(self, id: int, new_data: BaseModel):
		query = self.db.query(self.model).filter(self.model.id == id)
		db_item = query.first()
		if not db_item:
			raise NotFoundError(detail="Inventory was not found")
		exists = self.db.query(self.model).filter(self.model.id != id, self.model.name == new_data.name).count() > 0
		if exists:
			raise ValidationError(detail="An inventory with this name already exists")
		await pre_save.send(db_item)
		query.update(new_data.model_dump(), synchronize_session=False)
		self.db.commit()
		self.db.refresh(db_item)
		await post_save.send(db_item, created=False)
		return query.first()
