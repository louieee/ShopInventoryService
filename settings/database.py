from decouple import config
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def create_db():
	with engine.begin() as conn:
		from models import Product, ProductFile, Brand, Inventory, Staff, Customer, Order
		Base.metadata.create_all(bind=conn)
	engine.dispose()


def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()


Base.metadata.create_all(bind=engine)
