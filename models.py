from datetime import datetime

from sqlalchemy import ForeignKey, String, Text, Column, Integer, Float, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

import settings
from helpers.utilities import FileSaver
from settings.database import Base

file_saver = FileSaver(settings.UPLOAD_TYPE)



class BaseFile(Base):
	__abstract__ = True
	id: Mapped[int] = mapped_column(Integer, primary_key=True)
	name: Mapped[str] = mapped_column(String(length=200))
	url: Mapped[str] = mapped_column(String(length=256))  # Store the file path instead of content

	@classmethod
	def create(cls, name: str, url: str, **kwargs):
		file_record = cls(name=name, url=url, **kwargs)
		return file_record

	@classmethod
	def save(cls, name, content, **kwargs):
		extension = name.split(".")[-1]
		name = f"prod_image_{datetime.now().timestamp()}.{extension}"
		url = file_saver.save(folder=cls.upload_to, name=name, content=content)
		return cls.create(name, url, **kwargs)


	def delete_file(self):
		print("actual_url: ", self.url)
		return file_saver.delete(self.url)



class Inventory(Base):
	__tablename__ = "inventories"

	id: Mapped[int] = mapped_column(primary_key=True)
	name: Mapped[str] = mapped_column(String(100), unique=True)
	description: Mapped[str] = mapped_column(Text())
	date_of_acquisition: Mapped[datetime] = mapped_column(DateTime(timezone=True))
	location: Mapped[str] = mapped_column(String(100))
	products = relationship("Product", back_populates="inventory", cascade="all, delete-orphan")

	def __repr__(self) -> str:
		return f"Inventory(id={self.id!r}, name={self.name!r}"



class Product(Base):
	__tablename__ = "products"

	id: Mapped[int] = mapped_column(primary_key=True)
	name: Mapped[str] = mapped_column(String(100))
	description: Mapped[str] = mapped_column(Text())
	brand_id: Mapped[int] = Column(Integer, ForeignKey('brands.id'))
	brand = relationship("Brand", back_populates="products")
	inventory_id: Mapped[int] = Column(Integer, ForeignKey('inventories.id'))
	inventory = relationship("Inventory", back_populates="products")
	price: Mapped[float] = mapped_column(Float(precision=2))
	quantity: Mapped[int] = mapped_column(Integer())
	images = relationship("ProductFile", back_populates="product", cascade="all, delete-orphan")
	orders = relationship("Order", back_populates="product", cascade="all, delete-orphan")


class ProductFile(BaseFile):
	__tablename__ = "product_files"

	upload_to = "products"
	product_id: Mapped[int] = Column(Integer, ForeignKey('products.id'))
	product = relationship("Product", back_populates="images")


class Brand(Base):
	__tablename__ = "brands"

	id: Mapped[int] = mapped_column(primary_key=True)
	name: Mapped[str] = mapped_column(String(length=100))
	description: Mapped[str] = mapped_column(Text())
	products = relationship("Product", back_populates="brand", cascade="all, delete-orphan")



class Customer(Base):
	__tablename__ = "customers"

	id: Mapped[int] = mapped_column(primary_key=True)
	name: Mapped[str] = mapped_column(String(length=100))
	sales = relationship("Sale", back_populates="customer", cascade="all, delete-orphan")


class Staff(Base):
	__tablename__ = "staffs"

	id: Mapped[int] = mapped_column(primary_key=True)
	name: Mapped[str] = mapped_column(String(length=100))
	orders_processed = relationship("Order", back_populates="staff", cascade="all, delete-orphan")


class Order(Base):
	__tablename__ = "orders"

	id: Mapped[int] = mapped_column(primary_key=True)
	product_id: Mapped[int] = Column(Integer, ForeignKey("products.id"))
	product = relationship("Product", back_populates="orders")
	sale_id: Mapped[int] = Column(Integer, ForeignKey("sales.id"))
	sale = relationship("Sale", back_populates="orders")
	staff_id: Mapped[int] = Column(Integer, ForeignKey("staffs.id"))
	staff = relationship("Staff", back_populates="orders_processed")
	quantity: Mapped[int] = mapped_column(Integer())
	delivered: Mapped[bool] = mapped_column(Boolean())



class Sale(Base):
	__tablename__ = "sales"
	id: Mapped[int] = mapped_column(primary_key=True)
	paid: Mapped[bool] = mapped_column(Boolean())
	date_ordered: Mapped[datetime] = mapped_column(DateTime(timezone=True))
	date_paid: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True, default=None)
	customer_id: Mapped[int] = Column(Integer, ForeignKey("customers.id"))
	customer = relationship("Customer", back_populates="sales")
	location:Mapped[str] = mapped_column(Text())
	orders = relationship("Order", back_populates="sale",  cascade="all, delete-orphan")