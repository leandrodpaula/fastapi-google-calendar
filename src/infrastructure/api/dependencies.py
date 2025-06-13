from fastapi import Depends

from src.application.use_cases.create_event_use_case import CreateEventUseCase
from src.domain.repositories.event_repository import EventRepository
from src.application.services.google_calendar_service import GoogleCalendarService

from src.infrastructure.persistence.mongo_event_repository import MongoEventRepository
from src.infrastructure.external.google_calendar_adapter import GoogleCalendarAdapter
from src.infrastructure.config.mongo_config import get_mongo_settings, MongoSettings

# 1. Repository Provider
async def get_event_repository_dependency() -> EventRepository:
    settings: MongoSettings = get_mongo_settings()
    # In a real app, you might want to manage the client lifecycle (e.g. open/close connection)
    # For Motor, client is typically created once and reused.
    # MongoEventRepository now handles its own client.
    return MongoEventRepository(database_url=settings.MONGO_URI, database_name=settings.MONGO_DATABASE_NAME)

# 2. External Service Provider
async def get_google_calendar_service_dependency() -> GoogleCalendarService:
    # Add API key loading from config if it were a real service
    # settings = get_app_settings() # if you have general app settings
    # return GoogleCalendarAdapter(api_key=settings.GOOGLE_API_KEY)
    return GoogleCalendarAdapter() # Mock version, no API key needed

# 3. Use Case Provider
async def get_create_event_use_case_dependency(
    event_repo: EventRepository = Depends(get_event_repository_dependency),
    calendar_service: GoogleCalendarService = Depends(get_google_calendar_service_dependency)
) -> CreateEventUseCase:
    return CreateEventUseCase(event_repository=event_repo, google_calendar_service=calendar_service)
