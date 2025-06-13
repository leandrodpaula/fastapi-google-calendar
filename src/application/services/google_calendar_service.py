from abc import ABC, abstractmethod
from typing import Optional
import datetime

class GoogleCalendarService(ABC):
    """
    Interface for interacting with Google Calendar.
    """

    @abstractmethod
    async def create_event(
        self,
        title: str,
        start_datetime: datetime.datetime,
        end_datetime: datetime.datetime,
        description: Optional[str] = None
        # Add other relevant parameters like attendees, location, etc., as needed
    ) -> Optional[str]:
        """
        Creates an event in Google Calendar.
        Returns the Google Calendar event ID if successful, None otherwise.
        """
        pass

    # Add other methods as needed, e.g.:
    # @abstractmethod
    # async def get_event(self, google_event_id: str) -> Optional[dict]:
    #     pass
    #
    # @abstractmethod
    # async def update_event(self, google_event_id: str, event_data: dict) -> bool:
    #     pass
    #
    # @abstractmethod
    # async def delete_event(self, google_event_id: str) -> bool:
    #     pass
