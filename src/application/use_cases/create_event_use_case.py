from src.domain.entities.event import Event
from src.domain.repositories.event_repository import EventRepository
from src.application.services.google_calendar_service import GoogleCalendarService # Forward declaration

class CreateEventUseCase:
    def __init__(self, event_repository: EventRepository, google_calendar_service: GoogleCalendarService):
        self.event_repository = event_repository
        self.google_calendar_service = google_calendar_service

    async def execute(self, event_data: Event) -> Event:
        """
        Orchestrates event creation:
        1. Creates event in Google Calendar.
        2. Saves event to the internal repository with Google Calendar event ID.
        """
        # Step 1: Create event in Google Calendar
        # The actual implementation of how event_data is transformed to Google Calendar's
        # expected format would be within the google_calendar_service.
        # For now, we assume google_calendar_service.create_event returns the google_event_id

        google_event_id = await self.google_calendar_service.create_event(
            title=event_data.title,
            description=event_data.description,
            start_datetime=event_data.start_datetime,
            end_datetime=event_data.end_datetime
        )

        if not google_event_id:
            # Handle error: event creation failed in Google Calendar
            # This could raise a custom exception, log, or return a specific response
            # For simplicity, let's assume it might return None or raise an exception handled by the adapter
            raise Exception("Failed to create event in Google Calendar") # Or a more specific exception

        # Step 2: Update event data with Google Calendar event ID and save to repository
        event_data.google_event_id = google_event_id

        # The repository's save method should handle assigning a local ID if it's a new event
        saved_event = await self.event_repository.save(event_data)

        return saved_event
