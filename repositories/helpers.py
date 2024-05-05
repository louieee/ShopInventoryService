from typing import List, Optional

from fastapi import Query
from pydantic import BaseModel

import schemas.users
from helpers.exceptions import NotFoundError
from helpers.response import exception_quieter, SuccessResponse
from signals import post_save, pre_save, pre_delete


class BaseRepository:
	model = None
	db = None
	user:Optional[schemas.users.UserBase] = None

	def __init__(self, db, user=None):
		self.db = db
		self.user = user

	async def get(self, id: int, exists=False):
		query = self.db.query(self.model).filter(self.model.id == id)
		if exists:
			return query.count() > 0
		return query.first()

	async def get_all(self, skip: int = 0, limit: int = 100, **queries):
		queryset = await self.get_queryset(**queries)
		return queryset.offset(skip).limit(limit).all()

	async def get_queryset(self, queryset=None, **queries):
		if not queryset:
			queryset = self.db.query(self.model)
		if queries:
			queryset = queryset.filter_by(**queries)
		return queryset

	async def create(self, item: BaseModel, **kwargs):
		db_item = self.model(**item.model_dump())
		await pre_save.send(db_item)
		self.db.add(db_item)
		self.db.commit()
		self.db.refresh(db_item)
		await post_save.send(db_item, created=True)
		return db_item

	async def create_all(self, data_list: List[BaseModel]):
		instances = [self.model(**data.dict()) for data in data_list]
		self.db.bulk_save_objects(instances)
		self.db.commit()
		return instances

	async def update_all(self, ids: List[int], new_data: BaseModel):
		query = self.db.query(self.model).filter(self.model.id.in_(ids))
		query.update(new_data.dict(), synchronize_session=False)
		self.db.commit()
		return query.all()

	@exception_quieter
	async def update(self, id: int, new_data: BaseModel):
		query = self.db.query(self.model).filter(self.model.id == id)
		db_item = query.first()
		if not db_item:
			raise NotFoundError()
		await pre_save.send(db_item)
		query.update(new_data.model_dump(), synchronize_session=False)
		self.db.commit()
		self.db.refresh(db_item)
		await post_save.send(db_item, created=False)
		return query.first()

	@exception_quieter
	async def delete(self, id: int, **kwargs):
		query = self.db.query(self.model).filter(self.model.id == id)
		db_item = query.first()
		if not db_item:
			raise NotFoundError()
		await pre_delete.send(sender=db_item)
		query.delete(synchronize_session=False)
		self.db.commit()
		return SuccessResponse(status=204)

	async def delete_all(self, ids: List[int]):
		query = self.db.query(self.model).filter(self.model.id.in_(ids))
		deleted_rows = query.delete(synchronize_session=False)
		self.db.commit()
		return deleted_rows

	@staticmethod
	def delete_parameters(force: bool = Query(default=False,
	                                          description="if set to True, items would be deleted alongside their child items")):
		return {"force": force}














