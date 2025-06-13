import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock # For mocking dependencies
import datetime
from typing import Generator, Any

from src.main import app # Main FastAPI application
from src.domain.entities.event import Event as EventEntity
from src.application.use_cases.create_event_use_case import CreateEventUseCase
from src.domain.repositories.event_repository import EventRepository
from src.application.services.google_calendar_service import GoogleCalendarService

# --- Mock Dependencies Setup ---

@pytest.fixture
def mock_event_repository_integration() -> AsyncMock:
    return AsyncMock(spec=EventRepository)

@pytest.fixture
def mock_google_calendar_service_integration() -> AsyncMock:
    return AsyncMock(spec=GoogleCalendarService)

@pytest.fixture
def mock_create_event_use_case_integration(
    mock_event_repository_integration: AsyncMock,
    mock_google_calendar_service_integration: AsyncMock
) -> CreateEventUseCase:
    # We can either mock the use case directly, or provide its dependencies
    # For integration testing the endpoint, it's often better to provide a use case
    # that uses further mocks, or a real use case with mocked repo/service.
    # Let's use a real use case with mocked dependencies for this test.
    use_case = CreateEventUseCase(
        event_repository=mock_event_repository_integration,
        google_calendar_service=mock_google_calendar_service_integration
    )
    return AsyncMock(wraps=use_case) # Wrap in AsyncMock to spy on its execute method

# --- TestClient Fixture with Dependency Overrides ---

@pytest.fixture
def client(
    mock_create_event_use_case_integration: AsyncMock,
    mock_event_repository_integration: AsyncMock,
    mock_google_calendar_service_integration: AsyncMock
) -> Generator[TestClient, Any, None]:
    # Store original overrides
    original_overrides = app.dependency_overrides.copy()

    # Override dependencies for the TestClient
    app.dependency_overrides[CreateEventUseCase] = lambda: mock_create_event_use_case_integration
    # If CreateEventUseCase was not mocked but constructed with other mocks,
    # and those dependencies were also managed by FastAPI's DI:
    # app.dependency_overrides[EventRepository] = lambda: mock_event_repository_integration
    # app.dependency_overrides[GoogleCalendarService] = lambda: mock_google_calendar_service_integration

    with TestClient(app) as c:
        yield c

    # Clear or restore overrides after tests
    app.dependency_overrides = original_overrides


# --- Test Cases ---

@pytest.mark.asyncio
async def test_create_event_api_success(
    client: TestClient,
    mock_create_event_use_case_integration: AsyncMock,
    mock_event_repository_integration: AsyncMock,
    mock_google_calendar_service_integration: AsyncMock
):
    """
    Test successful event creation via the API endpoint.
    """
    event_payload = {
        "title": "Integration Test Event",
        "description": "Event for API integration testing",
        "start_datetime": "2024-08-15T10:00:00Z",
        "end_datetime": "2024-08-15T11:00:00Z"
    }

    fake_google_id = "gc_api_test_123"
    fake_repo_id = "repo_api_test_456"

    mock_create_event_use_case_integration.execute.return_value = EventEntity(
        id=fake_repo_id,
        google_event_id=fake_google_id,
        title=event_payload["title"],
        description=event_payload["description"],
        start_datetime=datetime.datetime.fromisoformat(event_payload["start_datetime"].replace("Z", "+00:00")),
        end_datetime=datetime.datetime.fromisoformat(event_payload["end_datetime"].replace("Z", "+00:00")),
        created_at=datetime.datetime.utcnow(), # Use actual datetime
        updated_at=datetime.datetime.utcnow()  # Use actual datetime
    )

    response = client.post("/api/v1/events/", json=event_payload)

    assert response.status_code == 201
    response_json = response.json()
    assert response_json["id"] == fake_repo_id
    assert response_json["google_event_id"] == fake_google_id
    assert response_json["title"] == event_payload["title"]
    # Timestamps are serialized, so compare them carefully if needed, or check for presence
    assert "created_at" in response_json
    assert "updated_at" in response_json

    mock_create_event_use_case_integration.execute.assert_called_once()
    # Optional: Check the argument passed to execute
    # called_arg = mock_create_event_use_case_integration.execute.call_args[0][0]
    # assert isinstance(called_arg, EventEntity)
    # assert called_arg.title == event_payload["title"]


@pytest.mark.asyncio
async def test_create_event_api_use_case_fails(
    client: TestClient,
    mock_create_event_use_case_integration: AsyncMock
):
    """
    Test API behavior when the CreateEventUseCase raises an exception.
    """
    event_payload = {
        "title": "Failing Event",
        "description": "This event will cause a use case failure",
        "start_datetime": "2024-08-16T10:00:00Z",
        "end_datetime": "2024-08-16T11:00:00Z"
    }

    mock_create_event_use_case_integration.execute.side_effect = Exception("Use case internal error")

    response = client.post("/api/v1/events/", json=event_payload)

    assert response.status_code == 500
    response_json = response.json()
    assert "detail" in response_json
    assert "Use case internal error" in response_json["detail"]

    mock_create_event_use_case_integration.execute.assert_called_once()
