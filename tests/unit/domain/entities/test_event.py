import pytest
from pydantic import ValidationError
import datetime

from src.domain.entities.event import Event
from src.domain.entities.participant import Participant

# Sample default data for an event (excluding participants)
DEFAULT_EVENT_DATA = {
    "title": "Test Event",
    "start_datetime": datetime.datetime(2024, 8, 15, 10, 0, 0, tzinfo=datetime.timezone.utc),
    "end_datetime": datetime.datetime(2024, 8, 15, 11, 0, 0, tzinfo=datetime.timezone.utc),
    "description": "A test event description."
}

def test_event_creation_with_participants():
    participant1_data = {"email": "p1@example.com", "cell_phone": "111000111"}
    participant2_data = {"cell_phone": "222000222"}

    participants_list = [Participant(**participant1_data), Participant(**participant2_data)]

    event_data = {**DEFAULT_EVENT_DATA, "participants": participants_list}
    event = Event(**event_data)

    assert event.title == DEFAULT_EVENT_DATA["title"]
    assert len(event.participants) == 2
    assert event.participants[0].email == participant1_data["email"]
    assert event.participants[1].cell_phone == participant2_data["cell_phone"]
    assert event.participants[1].email is None

def test_event_creation_with_empty_participants_list():
    event_data = {**DEFAULT_EVENT_DATA, "participants": []}
    event = Event(**event_data)

    assert event.title == DEFAULT_EVENT_DATA["title"]
    assert event.participants == []

def test_event_creation_with_participants_as_none():
    event_data = {**DEFAULT_EVENT_DATA, "participants": None} # Explicitly None
    event = Event(**event_data)

    assert event.title == DEFAULT_EVENT_DATA["title"]
    assert event.participants is None

def test_event_creation_with_participants_omitted():
    # Participants field is Optional, so it should default to None if not provided
    event_data_no_participants = {**DEFAULT_EVENT_DATA}
    event = Event(**event_data_no_participants)

    assert event.title == DEFAULT_EVENT_DATA["title"]
    assert event.participants is None # Default value for Optional field

def test_event_serialization_with_participants():
    participant1 = Participant(email="p1@example.com", cell_phone="111")
    participant2 = Participant(cell_phone="222")
    event = Event(**DEFAULT_EVENT_DATA, participants=[participant1, participant2])

    dumped_data = event.model_dump()

    assert dumped_data["title"] == DEFAULT_EVENT_DATA["title"]
    assert len(dumped_data["participants"]) == 2
    assert dumped_data["participants"][0]["email"] == "p1@example.com"
    assert dumped_data["participants"][0]["cell_phone"] == "111"
    assert dumped_data["participants"][1]["cell_phone"] == "222"
    assert dumped_data["participants"][1]["email"] is None # Ensure None is preserved

def test_event_deserialization_with_participants():
    participant_data_list = [
        {"email": "p1@example.com", "cell_phone": "111"},
        {"cell_phone": "222"} # email will be None
    ]
    raw_event_data = {
        **DEFAULT_EVENT_DATA,
        "participants": participant_data_list,
        # Pydantic will auto-convert ISO strings to datetime for these if not already objects
        "start_datetime": DEFAULT_EVENT_DATA["start_datetime"].isoformat(),
        "end_datetime": DEFAULT_EVENT_DATA["end_datetime"].isoformat()
    }

    event = Event.model_validate(raw_event_data)

    assert event.title == DEFAULT_EVENT_DATA["title"]
    assert len(event.participants) == 2
    assert event.participants[0].email == "p1@example.com"
    assert event.participants[0].cell_phone == "111"
    assert event.participants[1].cell_phone == "222"
    assert event.participants[1].email is None

def test_event_serialization_deserialization_cycle_with_participants():
    participant1 = Participant(email="cycle@example.com", cell_phone="000111")
    event_with_participants = Event(**DEFAULT_EVENT_DATA, participants=[participant1])

    dumped = event_with_participants.model_dump()
    reloaded_event = Event.model_validate(dumped)

    assert reloaded_event == event_with_participants
    assert reloaded_event.participants[0].email == "cycle@example.com"

def test_event_serialization_deserialization_cycle_participants_none():
    event_no_participants = Event(**DEFAULT_EVENT_DATA, participants=None)

    dumped = event_no_participants.model_dump()
    reloaded_event = Event.model_validate(dumped)

    assert reloaded_event == event_no_participants
    assert reloaded_event.participants is None

# Test for required fields (title, start_datetime, end_datetime)
def test_event_missing_required_fields():
    with pytest.raises(ValidationError):
        Event(start_datetime=DEFAULT_EVENT_DATA["start_datetime"], end_datetime=DEFAULT_EVENT_DATA["end_datetime"]) # Missing title
    with pytest.raises(ValidationError):
        Event(title="No start", end_datetime=DEFAULT_EVENT_DATA["end_datetime"]) # Missing start_datetime
    with pytest.raises(ValidationError):
        Event(title="No end", start_datetime=DEFAULT_EVENT_DATA["start_datetime"]) # Missing end_datetime

# Test that id, google_event_id, created_at, updated_at have defaults or are optional
def test_event_optional_and_default_fields():
    event = Event(**DEFAULT_EVENT_DATA)
    assert event.id is None # alias for _id, Optional
    assert event.google_event_id is None # Optional
    assert isinstance(event.created_at, datetime.datetime) # default_factory
    assert isinstance(event.updated_at, datetime.datetime) # default_factory
    assert event.description == DEFAULT_EVENT_DATA["description"] # Can be None
    assert event.participants is None # Optional

    # Test with description as None
    minimal_data = {
        "title": "Minimal Event",
        "start_datetime": datetime.datetime(2024, 1, 1, 12, 0, tzinfo=datetime.timezone.utc),
        "end_datetime": datetime.datetime(2024, 1, 1, 13, 0, tzinfo=datetime.timezone.utc),
    }
    event_minimal = Event(**minimal_data)
    assert event_minimal.description is None

    # Test id alias _id
    event_with_id = Event(**minimal_data, _id="custom_id_123")
    assert event_with_id.id == "custom_id_123"
    dumped_with_id = event_with_id.model_dump(by_alias=True)
    assert dumped_with_id["_id"] == "custom_id_123"
    assert "id" not in dumped_with_id # if by_alias=True and id is not explicitly in model for dump

    # To ensure 'id' is present in dump if needed (e.g. response models not using alias)
    # use event_with_id.model_dump() - this will use field names 'id'
    dumped_with_id_no_alias = event_with_id.model_dump()
    assert dumped_with_id_no_alias["id"] == "custom_id_123"

    # Test model_validate with _id
    validated_event = Event.model_validate({"_id": "mongo123", **minimal_data})
    assert validated_event.id == "mongo123"


# Test that created_at and updated_at are different if there's a slight delay (hard to test precisely without mocking time)
# For now, just check they are set.
# More advanced time testing: from freezegun import freeze_time
# @freeze_time("2024-01-01 12:00:00")
# def test_event_timestamps_with_freezegun(): ...
