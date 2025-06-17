import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock # For mocking dependencies
import datetime
from typing import Generator, Any, List

from src.main import app # Main FastAPI application
from src.domain.entities.event import Event as EventEntity
from src.domain.entities.participant import Participant # Added
from src.application.use_cases.create_event_use_case import CreateEventUseCase
# EventRepository and GoogleCalendarService might not be directly needed if CreateEventUseCase is fully mocked
# from src.domain.repositories.event_repository import EventRepository
# from src.application.services.google_calendar_service import GoogleCalendarService

# --- Mock Dependencies Setup ---
# Mocks for EventRepository and GoogleCalendarService are defined
# but might only be used if the CreateEventUseCase itself is NOT mocked but constructed with these.
# For the current setup where CreateEventUseCase is directly mocked, these are not strictly necessary
# for the client fixture, but good to have if test strategy changes.

# The mock_event_repository_integration and mock_google_calendar_service_integration
# are not strictly needed for the client fixture if CreateEventUseCase is fully mocked,
# but they are kept here for potential changes in testing strategy or if the use case
# mock needs to interact with them.
@pytest.fixture
def mock_event_repository_integration() -> AsyncMock:
    # This mock won't be directly verified in tests if CreateEventUseCase is fully mocked
    return AsyncMock(spec=EventRepository)

@pytest.fixture
def mock_google_calendar_service_integration() -> AsyncMock:
    # This mock won't be directly verified in tests if CreateEventUseCase is fully mocked
    return AsyncMock(spec=GoogleCalendarService)

@pytest.fixture
def mock_create_event_use_case_integration() -> AsyncMock:
    # Fully mock the use case. Its internal logic (calling repo/service) is unit tested elsewhere.
    # Here, we focus on endpoint -> use case interaction.
    return AsyncMock(spec=CreateEventUseCase)

# --- TestClient Fixture with Dependency Overrides ---

@pytest.fixture
def client(
    mock_create_event_use_case_integration: AsyncMock
) -> Generator[TestClient, Any, None]:
    original_overrides = app.dependency_overrides.copy()
    app.dependency_overrides[CreateEventUseCase] = lambda: mock_create_event_use_case_integration

    with TestClient(app) as c:
        yield c

    app.dependency_overrides = original_overrides


# --- Test Cases ---

@pytest.mark.asyncio
async def test_create_event_api_no_participants_success(
    client: TestClient,
    mock_create_event_use_case_integration: AsyncMock
):
    """
    Test successful event creation via API when no participants are provided.
    """
    event_payload = {
        "title": "Integration Test Event No Participants",
        "description": "Event for API integration testing",
        "start_datetime": "2024-08-15T10:00:00Z",
        "end_datetime": "2024-08-15T11:00:00Z",
        "participants": None # Explicitly None, or omit the field
    }

    fake_google_id = "gc_api_test_nop_123"
    fake_repo_id = "repo_api_test_nop_456"
    start_dt = datetime.datetime.fromisoformat(event_payload["start_datetime"].replace("Z", "+00:00"))
    end_dt = datetime.datetime.fromisoformat(event_payload["end_datetime"].replace("Z", "+00:00"))

    # Mock the return value of the use case's execute method
    mock_create_event_use_case_integration.execute.return_value = EventEntity(
        id=fake_repo_id,
        google_event_id=fake_google_id,
        title=event_payload["title"],
        description=event_payload["description"],
        start_datetime=start_dt,
        end_datetime=end_dt,
        participants=None, # Use case should return event with participants as None
        created_at=datetime.datetime.now(datetime.timezone.utc),
        updated_at=datetime.datetime.now(datetime.timezone.utc)
    )

    response = client.post("/api/v1/events/", json=event_payload)

    assert response.status_code == 201
    response_json = response.json()
    assert response_json["id"] == fake_repo_id
    assert response_json["google_event_id"] == fake_google_id
    assert response_json["title"] == event_payload["title"]
    assert response_json["participants"] is None # Expecting participants to be null or omitted
    assert "created_at" in response_json
    assert "updated_at" in response_json

    # Assert that the use case was called correctly
    mock_create_event_use_case_integration.execute.assert_called_once()
    called_event_arg = mock_create_event_use_case_integration.execute.call_args[0][0]
    assert isinstance(called_event_arg, EventEntity)
    assert called_event_arg.title == event_payload["title"]
    assert called_event_arg.participants is None # Endpoint should pass None for participants

@pytest.mark.asyncio
async def test_create_event_api_with_participants_success(
    client: TestClient,
    mock_create_event_use_case_integration: AsyncMock
):
    """
    Test successful event creation via API with participant data.
    """
    participant_payload_1 = {"email": "p1.api@example.com", "cell_phone": "111000111"}
    participant_payload_2 = {"cell_phone": "222000222"} # No email

    event_payload = {
        "title": "Integration Test Event With Participants",
        "description": "Event with participants for API integration testing",
        "start_datetime": "2024-08-16T10:00:00Z",
        "end_datetime": "2024-08-16T11:00:00Z",
        "participants": [participant_payload_1, participant_payload_2]
    }

    fake_google_id = "gc_api_test_wp_123"
    fake_repo_id = "repo_api_test_wp_456"
    start_dt = datetime.datetime.fromisoformat(event_payload["start_datetime"].replace("Z", "+00:00"))
    end_dt = datetime.datetime.fromisoformat(event_payload["end_datetime"].replace("Z", "+00:00"))

    # Expected Participant objects that the use case should receive
    expected_participants = [
        Participant(**participant_payload_1),
        Participant(**participant_payload_2)
    ]

    # Mock the return value of the use case's execute method
    mock_create_event_use_case_integration.execute.return_value = EventEntity(
        id=fake_repo_id,
        google_event_id=fake_google_id,
        title=event_payload["title"],
        description=event_payload["description"],
        start_datetime=start_dt,
        end_datetime=end_dt,
        participants=expected_participants, # Use case returns event with Participant objects
        created_at=datetime.datetime.now(datetime.timezone.utc),
        updated_at=datetime.datetime.now(datetime.timezone.utc)
    )

    response = client.post("/api/v1/events/", json=event_payload)

    assert response.status_code == 201
    response_json = response.json()
    assert response_json["id"] == fake_repo_id
    assert response_json["google_event_id"] == fake_google_id
    assert response_json["title"] == event_payload["title"]
    assert len(response_json["participants"]) == 2
    assert response_json["participants"][0]["email"] == participant_payload_1["email"]
    assert response_json["participants"][0]["cell_phone"] == participant_payload_1["cell_phone"]
    assert response_json["participants"][1]["email"] is None
    assert response_json["participants"][1]["cell_phone"] == participant_payload_2["cell_phone"]

    # Assert that the use case was called correctly
    mock_create_event_use_case_integration.execute.assert_called_once()
    called_event_arg = mock_create_event_use_case_integration.execute.call_args[0][0]
    assert isinstance(called_event_arg, EventEntity)
    assert called_event_arg.title == event_payload["title"]
    assert len(called_event_arg.participants) == 2
    # Compare participant objects (Pydantic models should be comparable if __eq__ is standard)
    assert called_event_arg.participants[0] == expected_participants[0]
    assert called_event_arg.participants[1] == expected_participants[1]


@pytest.mark.asyncio
async def test_create_event_api_invalid_participant_data(client: TestClient):
    """
    Test event creation with invalid participant data (e.g., missing cell_phone).
    The CreateEventUseCase should not even be called if request validation fails.
    """
    event_payload = {
        "title": "Event With Invalid Participant",
        "start_datetime": "2024-08-17T10:00:00Z",
        "end_datetime": "2024-08-17T11:00:00Z",
        "participants": [
            {"email": "p.valid@example.com", "cell_phone": "123"},
            {"email": "p.invalid@example.com"} # Missing cell_phone
        ]
    }

    response = client.post("/api/v1/events/", json=event_payload)

    assert response.status_code == 422 # Unprocessable Entity for Pydantic validation errors
    response_json = response.json()
    assert "detail" in response_json
    # Example error: {'loc': ['body', 'participants', 1, 'cell_phone'], 'msg': 'Field required', 'type': 'missing'}
    found_error = False
    for error in response_json["detail"]:
        if (error["loc"] == ['body', 'participants', 1, 'cell_phone'] and
            error["type"] == 'missing'):
            found_error = True
            break
    assert found_error, f"Expected cell_phone validation error not found in {response_json['detail']}"


@pytest.mark.asyncio
async def test_create_event_api_use_case_general_exception( # Renamed from test_create_event_api_use_case_fails
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
