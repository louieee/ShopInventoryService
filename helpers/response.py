import logging
from typing import List, Any

from fastapi import Query, Depends
from starlette.responses import JSONResponse, Response

from helpers.exceptions import AuthorizationError, ValidationError, NotFoundError, AuthenticationError


class SuccessResponse:
	"""Standardise API Responses and add additional keys"""

	def __new__(
			cls, data=None, message="successful", status=200, list_mode=False
	):
		return JSONResponse(
			{
				"status": True,
				"message": message,
				"data": data if data else [] if list_mode else {},
			},
			status,
		)


class FailureResponse:
	def __new__(cls, message="error", status=400):
		return JSONResponse({"status": False, "message": message}, status)


items = [f"Item {i}" for i in range(1, 1001)]


# Define a dependency function that returns the pagination parameters
def pagination_params(
		page: int = Query(1, gt=0),
		per_page: int = Query(10, gt=0)
):
	return {"page": page, "per_page": per_page}


def paginated_list(page: int, per_page: int, items: List[Any]):
	start = (page - 1) * per_page
	end = start + per_page
	return items[start:end]

def exception_quieter(func):
	async def inner(*args, **kwargs):
		try:
			return await func(*args, **kwargs)
		except (AuthenticationError, AuthorizationError, ValidationError, NotFoundError) as e:
			return FailureResponse(message=e.detail, status=e.status)
	return inner