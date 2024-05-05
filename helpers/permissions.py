from helpers.exceptions import AuthorizationError


def permission_access(customer:bool=True, admin:bool=True, staff:bool=True):
	def wrapper(func):
		async def inner(self, *args, **kwargs):
			if customer is False and self.user.is_customer is not None:
				raise AuthorizationError(detail="Customers are not allowed to perform this operation")
			if admin is False and self.user.is_admin is not None:
				raise AuthorizationError(detail="Admins are not allowed to perform this operation")
			if staff is False and self.user.is_staff is not None:
				raise AuthorizationError(detail="Staffs are not allowed to perform this operation")
			return await func(self, *args, **kwargs)
		return inner
	return wrapper