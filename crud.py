from sqlalchemy.orm import Session

import models
from helpers.security import get_hashed_password
from schemas import CreateUser
from signals import post_save


def get_user(db: Session, user_id: int, exists=False):
	query = db.query(models.User).filter(models.User.id == user_id)
	if exists:
		return query.exists().scalar()
	return query.first()


def get_user_by_email(db: Session, email: str, exists=False):
	query = db.query(models.User).filter(models.User.email == email)
	if exists:
		return db.query(query.exists()).scalar()
	return query.first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
	return db.query(models.User).offset(skip).limit(limit).all()


async def create_user(db: Session, user: CreateUser):
	fake_hashed_password = get_hashed_password(user.password)
	user.password = fake_hashed_password
	db_user = models.User(**user.dict())
	db.add(db_user)
	db.commit()
	db.refresh(db_user)
	await post_save.send(db_user)
	return db_user
