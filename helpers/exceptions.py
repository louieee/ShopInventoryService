from abc import ABC
from typing import Protocol


class CustomBaseException(Protocol):
	detail:str
	status:int






class AuthenticationError(BaseException, CustomBaseException):
	detail = "You are not authenticated"
	status = 401




class AuthorizationError(BaseException, CustomBaseException):
	detail = "You are not authorized to be here"
	status = 403

	def __init__(self, detail: str = None):
		super().__init__()
		if detail:
			self.detail = detail


class ValidationError(BaseException, CustomBaseException):
	detail = "Request Failed"
	status = 400

	def __init__(self, detail:str=None):
		super().__init__()
		if detail:
			self.detail = detail


class NotFoundError(BaseException, CustomBaseException):
	detail = "Not Found"
	status = 404

	def __init__(self, detail: str = None):
		super().__init__()
		if detail:
			self.detail = detail



