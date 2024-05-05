from sqlalchemy import or_

import models
from helpers.exceptions import ValidationError
from .helpers import *
from repositories.products import ProductRepository


class BrandRepository(BaseRepository):

	def __init__(self,*args, **kwargs):
		super().__init__(*args, **kwargs)
		self.model = models.Brand


	@staticmethod
	def query_parameters(search: str = Query(default=None, title="search", description="search for brands")):
		return {"search": search}

	async def get_all(self, skip: int = 0, limit: int = 100,
	                  search: str = None):
		queryset = await self.get_queryset()
		if search:
			queryset = queryset.filter(or_(self.model.name.icontains(search),
			                               self.model.description.icontains(search)))
		return {"count": queryset.count(), "results":queryset.offset(skip).limit(limit).all()}

	@exception_quieter
	async def delete(self, id: int, **kwargs):
		force: bool = kwargs.pop("force", False)
		if force is False:
			products = await ProductRepository(db=self.db, user=self.user) \
				.get_queryset(brand_id=id)
			if products.count() > 0:
				raise ValidationError("This brand still has products in it and therefore cannot be deleted")
		return await super(BrandRepository, self).delete(id)

	@exception_quieter
	async def create(self, item: BaseModel, **kwargs):
		# check if db has a branch with that name
		query = self.db.query(self.model).filter(self.model.name == str(item.name).title())
		exists = query.count() > 0
		if exists:
			raise ValidationError(detail="A branch with this name already exists")
		return await super(BrandRepository, self).create(item)

	@exception_quieter
	async def update(self, id: int, new_data: BaseModel):
		query = self.db.query(self.model).filter(self.model.id == id)
		db_item = query.first()
		if not db_item:
			raise NotFoundError(detail="Branch was not found")
		exists = self.db.query(self.model).filter(self.model.id != id, self.model.name == new_data.name).count() > 0
		if exists:
			raise ValidationError(detail="A branch with this name already exists")
		await pre_save.send(db_item)
		query.update(new_data.model_dump(), synchronize_session=False)
		self.db.commit()
		self.db.refresh(db_item)
		await post_save.send(db_item, created=False)
		return query.first()