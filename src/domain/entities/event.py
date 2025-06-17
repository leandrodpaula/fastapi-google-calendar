from typing import Optional, List
from pydantic import BaseModel, Field
import datetime

from src.domain.entities.participant import Participant

class Event(BaseModel):
    id: Optional[str] = Field(None, alias='_id') # MongoDB uses _id
    google_event_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    start_datetime: datetime.datetime
    end_datetime: datetime.datetime
    participants: Optional[List[Participant]] = None
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

    class Config:
        populate_by_name = True # Allows using '_id' in constructor for 'id'
        json_encoders = {
            datetime.datetime: lambda dt: dt.isoformat()
        }
        # Example for schema generation if needed
        # schema_extra = {
        #     "example": {
        #         "title": "Team Meeting",
        #         "description": "Weekly team sync",
        #         "start_datetime": "2024-08-15T10:00:00Z",
        #         "end_datetime": "2024-08-15T11:00:00Z"
        #     }
        # }
