import pytest
from unittest.mock import AsyncMock, MagicMock, call # For mocking async and regular methods, and call
import datetime

from src.application.use_cases.create_event_use_case import CreateEventUseCase
from src.domain.entities.event import Event
from src.domain.entities.participant import Participant # Added Participant import
from src.domain.repositories.event_repository import EventRepository
from src.application.services.google_calendar_service import GoogleCalendarService

@pytest.fixture
def mock_event_repository():
    return AsyncMock(spec=EventRepository)

@pytest.fixture
def mock_google_calendar_service():
    return AsyncMock(spec=GoogleCalendarService)

@pytest.fixture
def create_event_use_case(mock_event_repository, mock_google_calendar_service):
    return CreateEventUseCase(
        event_repository=mock_event_repository,
        google_calendar_service=mock_google_calendar_service
    )

@pytest.fixture
def sample_event_data() -> Event:
    return Event(
        title="Unit Test Event",
        description="Event for unit testing",
        start_datetime=datetime.datetime(2024, 8, 1, 10, 0, 0, tzinfo=datetime.timezone.utc),
        end_datetime=datetime.datetime(2024, 8, 1, 11, 0, 0, tzinfo=datetime.timezone.utc)
        # id, google_event_id, created_at, updated_at are not needed for creation input to use case
    )

@pytest.mark.asyncio
async def test_create_event_success(
    create_event_use_case: CreateEventUseCase,
    mock_event_repository: AsyncMock,
    mock_google_calendar_service: AsyncMock,
    sample_event_data: Event
):
    """
    Test successful event creation.
    Ensures Google Calendar service is called, then repository save is called,
    and the event with google_event_id is returned.
    """
    fake_google_event_id = "gc_12345"

    # Configure mocks
    mock_google_calendar_service.create_event.return_value = fake_google_event_id

    # When event_repository.save is called, it should return the event with google_event_id and its own id
    async def save_side_effect(event_to_save: Event):
        event_to_save.id = "repo_67890" # Simulate repository assigning an ID
        # google_event_id should already be set by the use case before calling save
        assert event_to_save.google_event_id == fake_google_event_id
        return event_to_save

    mock_event_repository.save.side_effect = save_side_effect

    # Execute the use case
    created_event = await create_event_use_case.execute(sample_event_data)

    # Assertions
    mock_google_calendar_service.create_event.assert_called_once_with(
        title=sample_event_data.title,
        description=sample_event_data.description,
        start_datetime=sample_event_data.start_datetime,
        end_datetime=sample_event_data.end_datetime,
        attendees=None # Explicitly pass None for attendees as per updated signature
    )

    # Check that the event passed to save has the google_event_id
    # The side_effect for save already has an assertion for this.
    # We can also check the call args directly if needed:
    # called_event_arg = mock_event_repository.save.call_args[0][0]
    # assert called_event_arg.google_event_id == fake_google_event_id

    mock_event_repository.save.assert_called_once_with(sample_event_data)

    assert created_event is not None
    assert created_event.id == "repo_67890"
    assert created_event.google_event_id == fake_google_event_id
    assert created_event.title == sample_event_data.title

@pytest.mark.asyncio
async def test_create_event_google_calendar_fails(
    create_event_use_case: CreateEventUseCase,
    mock_google_calendar_service: AsyncMock,
    mock_event_repository: AsyncMock,
    sample_event_data: Event
):
    """
    Test event creation when Google Calendar service fails.
    Ensures an exception is raised and repository save is not called.
    """
    # Configure mock: Google Calendar service returns None or raises an error
    # The use case currently raises Exception if google_event_id is None
    mock_google_calendar_service.create_event.return_value = None
    # Or: mock_google_calendar_service.create_event.side_effect = SomeCustomGoogleApiException("Failed")


    with pytest.raises(Exception, match="Failed to create event in Google Calendar"):
        await create_event_use_case.execute(sample_event_data)

    mock_google_calendar_service.create_event.assert_called_once()
    mock_event_repository.save.assert_not_called()


@pytest.fixture
def sample_participants_list() -> list[Participant]:
    return [
        Participant(email="test1@example.com", cell_phone="111222333"),
        Participant(cell_phone="444555666") # No email
    ]

@pytest.mark.asyncio
async def test_create_event_with_participants_success(
    create_event_use_case: CreateEventUseCase,
    mock_event_repository: AsyncMock,
    mock_google_calendar_service: AsyncMock,
    sample_event_data: Event, # Base event data without participants
    sample_participants_list: list[Participant]
):
    """
    Test successful event creation with participants.
    Ensures Google Calendar service is called with attendees and repository save includes participants.
    """
    fake_google_event_id = "gc_67890"
    event_with_participants = sample_event_data.model_copy(update={"participants": sample_participants_list})

    # Configure mocks
    mock_google_calendar_service.create_event.return_value = fake_google_event_id

    async def save_side_effect(event_to_save: Event):
        event_to_save.id = "repo_12345"
        assert event_to_save.google_event_id == fake_google_event_id
        assert event_to_save.participants == sample_participants_list # Key assertion for repo
        return event_to_save
    mock_event_repository.save.side_effect = save_side_effect

    # Execute the use case
    created_event = await create_event_use_case.execute(event_with_participants)

    # Assertions for Google Calendar Service call
    mock_google_calendar_service.create_event.assert_called_once_with(
        title=event_with_participants.title,
        description=event_with_participants.description,
        start_datetime=event_with_participants.start_datetime,
        end_datetime=event_with_participants.end_datetime,
        attendees=sample_participants_list # Key assertion for calendar service
    )

    # Assertions for Event Repository call (side effect already checks participants)
    mock_event_repository.save.assert_called_once_with(event_with_participants)

    # General assertions on the returned event
    assert created_event is not None
    assert created_event.id == "repo_12345"
    assert created_event.google_event_id == fake_google_event_id
    assert created_event.title == event_with_participants.title
    assert created_event.participants == sample_participants_list
