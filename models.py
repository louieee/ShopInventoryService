from typing import List
from sqlalchemy import ForeignKey, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from helpers.security import verify_password
from settings.database import Base


class User(Base):
	__tablename__ = "user"
	id: Mapped[int] = mapped_column(primary_key=True)
	first_name: Mapped[str] = mapped_column(String(50))
	last_name: Mapped[str] = mapped_column(String(50))
	password: Mapped[str] = mapped_column(String(150))
	email: Mapped[str] = mapped_column(String(30))
	is_admin: Mapped[bool] = mapped_column(Boolean(), default=False)
	addresses: Mapped[List["Address"]] = relationship(
		back_populates="user", cascade="all, delete-orphan"
	)

	def __repr__(self) -> str:
		return f"User(id={self.id!r}, name={self.first_name!r}"

	def check_password(self, password):
		return verify_password(password, self.password)




class Address(Base):
	__tablename__ = "address"
	id: Mapped[int] = mapped_column(primary_key=True)
	email_address: Mapped[str]
	user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
	user: Mapped["User"] = relationship(back_populates="addresses")

	def __repr__(self) -> str:
		return f"Address(id={self.id!r}, email_address={self.email_address!r})"
