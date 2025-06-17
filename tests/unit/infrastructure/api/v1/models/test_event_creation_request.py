import pytest
from pydantic import ValidationError
import datetime

from src.infrastructure.api.v1.endpoints.events import EventCreationRequest # Adjusted import path
from src.domain.entities.participant import Participant as ParticipantEntity # For constructing expected data

# Sample default data for an event request (excluding participants)
DEFAULT_EVENT_REQUEST_DATA = {
    "title": "API Test Event",
    "start_datetime": datetime.datetime(2024, 9, 1, 10, 0, 0, tzinfo=datetime.timezone.utc),
    "end_datetime": datetime.datetime(2024, 9, 1, 11, 0, 0, tzinfo=datetime.timezone.utc),
    "description": "An event created via API for testing."
}

# Sample valid participant data for requests
PARTICIPANT_DATA_VALID_1 = {"email": "api.p1@example.com", "cell_phone": "1001001001"}
PARTICIPANT_DATA_VALID_2 = {"cell_phone": "2002002002"} # Email is optional

# Sample invalid participant data for requests
PARTICIPANT_DATA_INVALID_NO_CELL = {"email": "api.p_invalid@example.com"}


def test_event_creation_request_valid_with_participants():
    request_data = {
        **DEFAULT_EVENT_REQUEST_DATA,
        "participants": [PARTICIPANT_DATA_VALID_1, PARTICIPANT_DATA_VALID_2]
    }

    try:
        model = EventCreationRequest(**request_data)
        assert model.title == DEFAULT_EVENT_REQUEST_DATA["title"]
        assert len(model.participants) == 2
        # Pydantic should convert dicts to Participant models if type hint is List[Participant]
        assert isinstance(model.participants[0], ParticipantEntity)
        assert model.participants[0].email == PARTICIPANT_DATA_VALID_1["email"]
        assert model.participants[0].cell_phone == PARTICIPANT_DATA_VALID_1["cell_phone"]
        assert isinstance(model.participants[1], ParticipantEntity)
        assert model.participants[1].email is None
        assert model.participants[1].cell_phone == PARTICIPANT_DATA_VALID_2["cell_phone"]
    except ValidationError as e:
        pytest.fail(f"Validation failed unexpectedly: {e.errors()}")

def test_event_creation_request_valid_participants_empty_list():
    request_data = {**DEFAULT_EVENT_REQUEST_DATA, "participants": []}
    try:
        model = EventCreationRequest(**request_data)
        assert model.participants == []
    except ValidationError as e:
        pytest.fail(f"Validation failed unexpectedly for empty participants list: {e.errors()}")

def test_event_creation_request_valid_participants_none():
    request_data = {**DEFAULT_EVENT_REQUEST_DATA, "participants": None}
    try:
        model = EventCreationRequest(**request_data)
        assert model.participants is None
    except ValidationError as e:
        pytest.fail(f"Validation failed unexpectedly for participants=None: {e.errors()}")

def test_event_creation_request_valid_participants_omitted():
    # Participants field itself is optional in EventCreationRequest
    request_data = {**DEFAULT_EVENT_REQUEST_DATA}
    try:
        model = EventCreationRequest(**request_data)
        assert model.participants is None # Should default to None
    except ValidationError as e:
        pytest.fail(f"Validation failed unexpectedly when participants field is omitted: {e.errors()}")


def test_event_creation_request_invalid_participant_missing_cell_phone():
    request_data = {
        **DEFAULT_EVENT_REQUEST_DATA,
        "participants": [PARTICIPANT_DATA_VALID_1, PARTICIPANT_DATA_INVALID_NO_CELL]
    }

    with pytest.raises(ValidationError) as excinfo:
        EventCreationRequest(**request_data)

    errors = excinfo.value.errors()
    # Example error structure:
    # [{'type': 'missing', 'loc': ('participants', 1, 'cell_phone'), 'msg': 'Field required', ...}]
    assert len(errors) == 1
    error = errors[0]
    assert error['type'] == 'missing'
    assert error['loc'] == ('participants', 1, 'cell_phone') # participants -> list index 1 -> cell_phone field

def test_event_creation_request_invalid_participant_data_type():
    # Example: participant is not a dict, or a field has wrong type
    request_data_bad_type = {
        **DEFAULT_EVENT_REQUEST_DATA,
        "participants": [PARTICIPANT_DATA_VALID_1, "not_a_participant_object"]
    }
    with pytest.raises(ValidationError) as excinfo:
        EventCreationRequest(**request_data_bad_type)

    errors = excinfo.value.errors()
    # Example error: [{'type': 'model_attributes_type', 'loc': ('participants', 1), 'msg': 'Input should be a valid dictionary or instance of Participant', ...}]
    # OR if Participant is used directly: [{'type': 'dataclass_type', 'loc': ('participants', 1), 'msg': 'Input should be a valid dictionary or instance of Participant', ...}]
    # For Pydantic v2 and List[Participant], it expects dicts that can be parsed into Participant
    assert any(err['loc'] == ('participants', 1) and 'Input should be a valid dictionary' in err['msg'] for err in errors)


def test_event_creation_request_base_fields_validation():
    # Test that base fields are still validated
    with pytest.raises(ValidationError) as excinfo:
        EventCreationRequest(start_datetime="not a datetime", end_datetime="also not a datetime")

    errors = excinfo.value.errors()
    assert any(err['loc'] == ('title',) and err['type'] == 'missing' for err in errors)
    assert any(err['loc'] == ('start_datetime',) and 'valid datetime format' in err['msg'] for err in errors) # Pydantic v2 msg
    assert any(err['loc'] == ('end_datetime',) and 'valid datetime format' in err['msg'] for err in errors)

def test_event_creation_request_participant_email_can_be_empty_string():
    # Assuming Participant model (used in EventCreationRequest) allows empty string for email
    # (since it's Optional[str], not EmailStr which would forbid "")
    participant_empty_email = {"email": "", "cell_phone": "3003003003"}
    request_data = {
        **DEFAULT_EVENT_REQUEST_DATA,
        "participants": [participant_empty_email]
    }
    try:
        model = EventCreationRequest(**request_data)
        assert model.participants[0].email == ""
    except ValidationError as e:
        pytest.fail(f"Validation failed for participant with empty string email: {e.errors()}")

# Check if schema_extra example is valid
def test_event_creation_request_schema_example_is_valid():
    example_data = EventCreationRequest.Config.schema_extra["example"]
    try:
        EventCreationRequest(**example_data)
    except ValidationError as e:
        pytest.fail(f"Schema example is not valid: {e.errors()}")

# Test with datetime strings as they would come in JSON
def test_event_creation_request_with_datetime_strings():
    request_data_dt_strings = {
        "title": "Event with DT Strings",
        "start_datetime": "2024-10-01T10:00:00Z", # ISO format
        "end_datetime": "2024-10-01T11:00:00+00:00", # ISO format with offset
        "participants": [{"cell_phone": "5555555555"}]
    }
    try:
        model = EventCreationRequest(**request_data_dt_strings)
        assert model.start_datetime == datetime.datetime(2024, 10, 1, 10, 0, 0, tzinfo=datetime.timezone.utc)
        assert model.end_datetime == datetime.datetime(2024, 10, 1, 11, 0, 0, tzinfo=datetime.timezone.utc)
        assert len(model.participants) == 1
    except ValidationError as e:
        pytest.fail(f"Validation failed with datetime strings: {e.errors()}")

# If Participant model itself uses pydantic.EmailStr for email field,
# then invalid email formats would be caught.
# Our current Participant uses Optional[str], so format is not strictly enforced by Pydantic beyond being a string.
# If strict email validation is needed at API layer, EventCreationRequest.ParticipantSchema.email could use EmailStr.
# For now, this test acknowledges that any string (or None) is accepted by Participant.email.
def test_event_creation_request_participant_email_any_string():
    participant_any_string_email = {"email": "not-really-an-email", "cell_phone": "4004004004"}
    request_data = {
        **DEFAULT_EVENT_REQUEST_DATA,
        "participants": [participant_any_string_email]
    }
    try:
        model = EventCreationRequest(**request_data)
        assert model.participants[0].email == "not-really-an-email"
    except ValidationError as e:
        pytest.fail(f"Validation failed for participant with non-email-format string: {e.errors()}")

    # If Participant.email was EmailStr, this would fail:
    # from pydantic import EmailStr
    # class ParticipantWithEmailStr(BaseModel): email: Optional[EmailStr] = None; cell_phone: str
    # with pytest.raises(ValidationError): ParticipantWithEmailStr(email="invalid", cell_phone="123")
    # This is a design note rather than a test for current code.
