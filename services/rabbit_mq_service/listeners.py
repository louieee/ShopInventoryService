import asyncio
import json
from typing import Optional

from fastapi import Depends
from sqlalchemy.orm import Session

from repositories.users import CustomerRepository, StaffRepository
from schemas.users import CustomerBase, StaffBase
from services.rabbit_mq_service.data import UserPayload
from settings.database import get_db, SessionLocal


class UserListener:

	@classmethod
	def handle_user_data(cls, action: str, data: str):
		# print("message: ", data)
		data = cls._convert_data(data)
		if not data:
			return
		print("message: ", data.__dict__)

		db: Session = SessionLocal()
		if action == "create":
			cls._handle_create_user(db=db, user=data)
		elif action == "update":
			cls._handle_update_user(db=db, user=data)
		elif action == "delete":
			cls._handle_delete_user(db=db, user=data)
		db.close()
		return

	@classmethod
	def _convert_data(cls, data: str) -> Optional[UserPayload]:
		try:
			data = json.loads(data)
			return UserPayload(**data)
		except Exception as e:
			print(e)
			return None

	@classmethod
	def _handle_create_user(cls, db: Session, user: UserPayload):
		if user.is_customer and user.customer_id:
			customer = CustomerBase(id=user.customer_id,
			                        name=f"{user.first_name} {user.last_name}")
			asyncio.run(CustomerRepository(db=db).create(item=customer))
		elif user.is_staff and user.staff_id:
			staff = StaffBase(id=user.staff_id,
			                  name=f"{user.first_name} {user.last_name}")
			asyncio.run(StaffRepository(db=db).create(item=staff))

	@classmethod
	def _handle_update_user(cls, db: Session, user: UserPayload):
		if user.is_customer and user.customer_id:
			customer = CustomerBase(id=user.customer_id,
			                        name=f"{user.first_name} {user.last_name}")
			asyncio.run(CustomerRepository(db=db).update(new_data=customer, id=customer.id))
		elif user.is_staff and user.staff_id:
			staff = StaffBase(id=user.staff_id,
			                  name=f"{user.first_name} {user.last_name}")
			asyncio.run(StaffRepository(db=db).update(new_data=staff, id=staff.id))

	@classmethod
	def _handle_delete_user(cls, db: Session, user: UserPayload):
		if user.is_customer and user.customer_id:
			customer = CustomerBase(id=user.customer_id,
			                        name=f"{user.first_name} {user.last_name}")
			asyncio.run(CustomerRepository(db=db).delete(id=customer.id))
		elif user.is_staff and user.staff_id:
			staff = StaffBase(id=user.staff_id,
			                  name=f"{user.first_name} {user.last_name}")
			asyncio.run(StaffRepository(db=db).delete(id=staff.id))
