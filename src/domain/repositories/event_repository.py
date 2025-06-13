from abc import ABC, abstractmethod
from typing import Optional, List
from src.domain.entities.event import Event

class EventRepository(ABC):
    """
    Interface for event persistence operations.
    """

    @abstractmethod
    async def save(self, event: Event) -> Event:
        """
        Saves an event to the repository.
        If the event has an ID, it should be updated, otherwise created.
        Returns the saved event (potentially with an ID assigned).
        """
        pass

    @abstractmethod
    async def find_by_id(self, event_id: str) -> Optional[Event]:
        """
        Finds an event by its ID.
        Returns the event or None if not found.
        """
        pass

    @abstractmethod
    async def find_all(self) -> List[Event]:
        """
        Returns all events.
        """
        pass

    @abstractmethod
    async def delete_by_id(self, event_id: str) -> bool:
        """
        Deletes an event by its ID.
        Returns True if deleted, False otherwise.
        """
        pass
