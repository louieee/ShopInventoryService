from fastapi import Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

import models
from helpers.exceptions import ValidationError, NotFoundError
from helpers.response import exception_quieter
from repositories.base import BaseRepository
from signals.helpers import pre_save, post_save


class CustomerRepository(BaseRepository):

	def __init__(self, db: Session, user=None):
		super().__init__(db=db, user=user)
		self.model = models.Customer



	@staticmethod
	def query_parameters(search: str = Query(default=None, title="search", description="search for brands")):
		return {"search": search}


	@exception_quieter
	async def create(self, item: BaseModel, **kwargs):
		query = self.db.query(self.model).filter(self.model.id == item.id)
		exists = query.count() > 0
		if exists:
			raise ValidationError(detail="A customer with this id already exists")
		return await super(CustomerRepository, self).create(item)

	@exception_quieter
	async def update(self, id: int, new_data: BaseModel):
		query = self.db.query(self.model).filter(self.model.id == id)
		db_item = query.first()
		if not db_item:
			raise NotFoundError(detail="Customer was not found")
		await pre_save.send(db_item)
		query.update(new_data.model_dump(), synchronize_session=False)
		self.db.commit()
		self.db.refresh(db_item)
		await post_save.send(db_item, created=False)
		return query.first()


class StaffRepository(BaseRepository):

	def __init__(self,*args, **kwargs):
		super().__init__(*args, **kwargs)
		self.model = models.Staff


	@staticmethod
	def query_parameters(search: str = Query(default=None, title="search", description="search for brands")):
		return {"search": search}


	@exception_quieter
	async def create(self, item: BaseModel, **kwargs):
		query = self.db.query(self.model).filter(self.model.id == item.id)
		exists = query.count() > 0
		if exists:
			raise ValidationError(detail="A staff with this id already exists")
		return await super(StaffRepository, self).create(item)

	@exception_quieter
	async def update(self, id: int, new_data: BaseModel):
		query = self.db.query(self.model).filter(self.model.id == id)
		db_item = query.first()
		if not db_item:
			raise NotFoundError(detail="staff was not found")
		await pre_save.send(db_item)
		query.update(new_data.model_dump(), synchronize_session=False)
		self.db.commit()
		self.db.refresh(db_item)
		await post_save.send(db_item, created=False)
		return query.first()