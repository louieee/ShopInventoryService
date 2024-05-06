from typing import Optional

from pydantic import BaseModel


class DefaultResponse(BaseModel):
	status: bool
	message: str

class SuccessResponse(DefaultResponse):
	data: Optional[dict|list]