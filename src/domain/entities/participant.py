from typing import Optional

from pydantic import BaseModel, Field


class Participant(BaseModel):
    email: Optional[str] = Field(None)
    cell_phone: str
