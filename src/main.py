from fastapi import FastAPI, Depends

from src.infrastructure.api.v1.endpoints import events as events_v1_router
from src.application.use_cases.create_event_use_case import CreateEventUseCase
from src.domain.repositories.event_repository import EventRepository
from src.application.services.google_calendar_service import GoogleCalendarService

# These will be concrete implementations from infrastructure
from src.infrastructure.persistence.mongo_event_repository import MongoEventRepository # Placeholder
from src.infrastructure.external.google_calendar_adapter import GoogleCalendarAdapter # Placeholder
from src.infrastructure.config.mongo_config import get_mongo_settings
from src.infrastructure.api.dependencies import get_create_event_use_case_dependency, get_event_repository_dependency, get_google_calendar_service_dependency

# --- Dependency Injection Setup ---
# (This is a simplified setup. For larger apps, consider a dependencies module)

# Configuration (placeholders, real config would be loaded from env, files, etc.)
# Example: MONGO_URL = "mongodb://localhost:27017"
# Example: MONGO_DB_NAME = "event_planner_db"

# In a real app, get_mongo_settings would load from environment or a config file.
# For now, we'll use a dummy version if mongo_config.py is not fully implemented yet.

# 1. Repository Provider
# --- FastAPI App Initialization ---
app = FastAPI(
    title="Event Management API",
    version="0.1.0",
    description="API for managing events with Google Calendar integration and MongoDB persistence, using Onion Architecture."
)

# Include routers
app.include_router(events_v1_router.router)

# Override dependencies for FastAPI
# This tells FastAPI how to resolve CreateEventUseCase when it sees Depends() or Annotated[..., Depends()]
app.dependency_overrides[CreateEventUseCase] = get_create_event_use_case_dependency
# We can also override the repository and service dependencies directly if other components need them
app.dependency_overrides[EventRepository] = get_event_repository_dependency
app.dependency_overrides[GoogleCalendarService] = get_google_calendar_service_dependency


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}

# To run this app (after installing uvicorn and fastapi):
# uvicorn src.main:app --reload

# Note: MongoEventRepository and GoogleCalendarAdapter need to be implemented
# for the dependency injection to fully work. For now, they are placeholders.
# If they are not implemented yet, trying to run the app and hit the endpoint will fail.
# We will implement them in the subsequent steps.
