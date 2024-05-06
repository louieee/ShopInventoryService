import logging
from datetime import datetime
from typing import List

from fastapi import Query
from pydantic import BaseModel
from sqlalchemy import text

import models
from helpers.exceptions import ValidationError, NotFoundError, AuthorizationError
from helpers.permissions import permission_access
from helpers.response import FailureResponse, exception_quieter, SuccessResponse
from repositories.helpers import BaseRepository
from schemas import sales as schemas
from signals import pre_save, post_save, pre_delete


class SaleRepository(BaseRepository):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.model = models.Sale

	@staticmethod
	def query_parameters(paid: bool = Query(default=None, title="paid", description="filter by paid or non paid sales"),
	                     search: str = Query(default=None, title="search", description="search for customer and/or location"),
	                     date_ordered_start: datetime = Query(default=None, title="date_ordered_start",
	                                                description=" start date for date ordered"),
	                     date_ordered_stop: datetime = Query(default=None, title="ate_ordered_stop",
	                                              description="end date for date ordered"),
	                     date_paid_start: datetime = Query(default=None, title="date_paid_start",
	                                                          description=" start date for date paid"),
	                     date_paid_stop: datetime = Query(default=None, title="date_paid_stop",
	                                                         description="end date for date paid")
	                     ):
		if date_ordered_start:
			date_ordered_start = datetime.strptime(str(date_ordered_start), "%Y-%m-%d %H:%M:%S", )
		if date_ordered_stop:
			date_ordered_stop = datetime.strptime(str(date_ordered_stop), "%Y-%m-%d %H:%M:%S", )
		if date_paid_start:
			date_paid_start = datetime.strptime(str(date_paid_start), "%Y-%m-%d %H:%M:%S", )
		if date_paid_stop:
			date_paid_stop = datetime.strptime(str(date_paid_stop), "%Y-%m-%d %H:%M:%S", )


		return {"paid": paid, "search": search,
		        "date_ordered_stop": date_ordered_stop, "date_ordered_start": date_ordered_start,
		        "date_paid_stop": date_paid_stop, "date_paid_start": date_paid_start,
		        }

	@exception_quieter
	async def create(self, item: schemas.CreateSale, **kwargs):
		data = item.model_dump()
		orders = data.pop("orders")
		product_ids = [order['product_id'] for order in orders]
		product_count = self.db.query(models.Product).filter(models.Product.id.in_(product_ids)).count()
		if len(product_ids) != product_count:
			raise ValidationError(detail="You have non existent products in this orders")
		data["date_ordered"] = datetime.now()
		sale = self.model(**data)
		await pre_save.send(sale)
		self.db.add(sale)
		self.db.commit()
		self.db.refresh(sale)
		orders = [models.Order(**order, sale_id=sale.id) for order in orders]
		self.db.bulk_save_objects(orders)
		self.db.commit()
		self.db.refresh(sale)
		await post_save.send(sale, created=True)
		return SuccessResponse(message="Sale created successfully")


	async def update(self, id: int, new_data: BaseModel):
		return FailureResponse(message="Sale cannot be updated")

	@exception_quieter
	async def add_orders(self, id:int, orders: List[schemas.OrderItem]):
		sale:models.Sale = await self.get(id=id)
		if not sale:
			raise NotFoundError(detail="This Sale does not exist")
		if sale.paid:
			raise ValidationError(detail="This sale is already paid for. Please create another sale.")
		orders = [models.Order(**order.model_dump(), sale_id=id) for order in orders]
		product_ids = [order.product_id for order in orders]
		product_count = self.db.query(models.Product).filter(models.Product.id.in_(product_ids)).count()
		if len(product_ids) != product_count:
			raise ValidationError(detail="You have non existent products in this orders")
		self.db.bulk_save_objects(orders)
		self.db.commit()
		self.db.refresh(sale)
		return SuccessResponse(message="Orders added successfully")


	@exception_quieter
	async def remove_orders(self, id:int, order_ids: List[int]):
		sale: models.Sale = await self.get(id=id)
		if not sale:
			raise NotFoundError(detail="This Sale does not exist")
		if sale.paid:
			raise ValidationError(detail="This sale is already paid for and cannot be edited")
		querystring = text("delete from orders where sale_id = :id and id in :order_ids")
		self.db.execute(querystring, {"id": id, "order_ids": order_ids})
		self.db.commit()
		self.db.refresh(sale)
		return SuccessResponse(message="Selected Orders have been removed successfully")

	@exception_quieter
	async def mark_paid(self, id:int):
		sale: models.Sale = await self.get(id=id)
		if not sale:
			raise NotFoundError(detail="This Sale does not exist")
		if sale.paid:
			return sale
		await pre_save.send(sale)
		querystring = text("update sales set paid = true, date_paid = :now where id = :id")
		self.db.execute(querystring, {"id": id, "now": datetime.now()})
		self.db.commit()
		self.db.refresh(sale)
		await post_save.send(sale, created=False)
		return SuccessResponse(message="Sale has been successfully marked as paid")

	@exception_quieter
	@permission_access(admin=False, staff=False)
	async def delete(self, id: int, **kwargs):
		sale = await self.get(id=id)
		if not sale:
			raise NotFoundError(detail="This Sale does not exist")
		if sale.paid:
			raise ValidationError(detail="This sale has been paid for and therefore cannot be deleted")
		if self.user.customer_id == sale.customer_id:
			raise AuthorizationError(detail="You are not the owner of this sale")
		await pre_delete.send(sale)
		querystring = text("delete from sales where id = :id")
		self.db.execute(querystring, {"id": id})
		self.db.commit()
		return SuccessResponse(status=204)


	async def get_by_id(self, id: int):
		querystring = text("select * from sales_view where id = :id ;")
		sale_detail = dict(self.db.execute(querystring, {"id": id}).mappings().first())
		querystring = text("select * from orders_view where sale_id = :id ;")
		orders = self.db.execute(querystring, {"id": id}).mappings().all()
		sale_detail["orders"] = orders
		return sale_detail


	async def get_all(self, skip: int = 0, limit: int = 100, search:str=None, paid:bool=None,
	                  date_ordered_start:datetime=None, date_ordered_stop:datetime=None,
	                  date_paid_start:datetime=None, date_paid_stop:datetime=None):
		querystring = "select * from sales_view"
		params = dict()
		if search:
			querystring = f"{querystring} {'where' if 'where' not in querystring else 'and'} location ilike :search or customer ilike :search"
			params["search"] = f"%{search}%"
		if paid is not None:
			querystring = f"{querystring} {'where' if 'where' not in querystring else 'and'} paid = :paid"
			params["paid"] = paid
		if date_ordered_start and date_ordered_stop:
			querystring = f"{querystring} {'where' if 'where' not in querystring else 'and'} date_ordered >= :date_ordered_start and date_ordered <= :date_ordered_end"
			params["date_ordered_start"] = date_ordered_start
			params["date_ordered_end"] = date_ordered_stop
		if date_paid_start and date_paid_stop:
			querystring = f"{querystring} {'where' if 'where' not in querystring else 'and'} date_paid >= :date_paid_start and date_paid <= :date_paid_end"
			params["date_paid_start"] = date_paid_start
			params["date_paid_end"] = date_paid_stop

		count = self.db.execute(text(f"{querystring.replace('select *', 'select count(*)', 1)};"), params).mappings().first()["count"]
		querystring = f"{querystring} offset :skip limit :limit ;"
		params["skip"] = skip
		params["limit"] = limit
		return {"count": count, "results": self.db.execute(text(querystring), params).mappings().all()}


	@exception_quieter
	@permission_access(customer=False, admin=False)
	async def mark_order_as_delivered(self, order_id:int):
		order = self.db.query(models.Order).filter(models.Order.id == order_id).first()
		if not order:
			raise NotFoundError(detail="This order does not exist")
		if order.staff_id is None:
			raise NotFoundError(detail="This order has no staff assigned to it")
		if order.staff_id  != self.user.staff_id:
			raise AuthorizationError(detail="You are not assigned to this order")
		querystring = "update orders set delivered = true, date_delivered = :now where id = :order_id ;"
		self.db.execute(text(querystring), {"order_id": order_id, "now": datetime.now()})
		self.db.commit()
		return SuccessResponse(message="This order has been successfully marked as delivered")

	@exception_quieter
	@permission_access(customer=False, staff=False)
	async def assign_staff_to_orders(self, staff_id:int, order_ids:List[int]):
		orders_with_staffs = self.db.query(models.Order).filter(models.Order.id.in_(order_ids), models.Order.staff_id != None).count() > 0
		if orders_with_staffs:
			raise ValidationError(detail="Some selected orders already have staffs assigned to them")

		delivered_orders = self.db.query(models.Order).filter(models.Order.id.in_(order_ids), models.Order.delivered == True).count() > 0
		if delivered_orders:
			raise ValidationError(detail="Some selected orders are already delivered and cannot be updated")

		querystring = "update orders set staff_id = :staff_id where id in :ids ;"
		self.db.execute(text(querystring), {"staff_id": staff_id, "ids": order_ids})
		self.db.commit()
		return SuccessResponse(message="Staffs have been successfully assigned to selected orders")

	@exception_quieter
	@permission_access(customer=False, staff=False)
	async def remove_staff_from_orders(self, staff_id: int, order_ids: List[int]):
		delivered_orders = self.db.query(models.Order).filter(models.Order.id.in_(order_ids),
		                                                      models.Order.delivered == True).count() > 0
		if delivered_orders:
			raise ValidationError(detail="Some selected orders are already delivered and cannot be updated")

		querystring = "update orders set staff_id = NULL where id in :ids ;"
		self.db.execute(text(querystring), {"staff_id": staff_id, "ids": order_ids})
		self.db.commit()
		return SuccessResponse(message="Staffs have been successfully removed from the selected orders")








