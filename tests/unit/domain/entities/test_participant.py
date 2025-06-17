import pytest
from pydantic import ValidationError

from src.domain.entities.participant import Participant

def test_participant_creation_with_email_and_cell():
    participant_data = {"email": "test@example.com", "cell_phone": "1234567890"}
    participant = Participant(**participant_data)
    assert participant.email == participant_data["email"]
    assert participant.cell_phone == participant_data["cell_phone"]

def test_participant_creation_with_cell_only():
    participant_data = {"cell_phone": "1234567890"}
    participant = Participant(**participant_data)
    assert participant.email is None
    assert participant.cell_phone == participant_data["cell_phone"]

def test_participant_creation_cell_optional_email_provided():
    # This test ensures that if email is provided, it's captured, even if None was default for field
    participant_data = {"email": "test@example.com", "cell_phone": "1234567890"}
    participant = Participant(**participant_data)
    assert participant.email == "test@example.com"

    participant_data_no_email = {"cell_phone": "0987654321"}
    participant_no_email = Participant(**participant_data_no_email)
    assert participant_no_email.email is None


def test_participant_missing_cell_phone_raises_validation_error():
    with pytest.raises(ValidationError) as excinfo:
        Participant(email="test@example.com")

    assert "cell_phone" in str(excinfo.value)
    # Check that the error message indicates 'cell_phone' is missing
    # Example: [{'type': 'missing', 'loc': ('cell_phone',), 'msg': 'Field required', ...}]
    errors = excinfo.value.errors()
    assert any(err['type'] == 'missing' and 'cell_phone' in err['loc'] for err in errors)

def test_participant_cell_phone_is_mandatory():
    with pytest.raises(ValidationError):
        Participant(email="test@example.com") # cell_phone is missing

    # Should not raise error
    try:
        Participant(cell_phone="1234567890")
    except ValidationError:
        pytest.fail("ValidationError raised unexpectedly when cell_phone is provided.")

def test_participant_email_can_be_none_explicitly():
    participant_data = {"email": None, "cell_phone": "1234567890"}
    participant = Participant(**participant_data)
    assert participant.email is None
    assert participant.cell_phone == participant_data["cell_phone"]

def test_participant_empty_string_email_is_valid_if_not_none():
    # Pydantic's EmailStr would validate format, but we used str, so empty string is fine
    # If EmailStr were used, "" would be invalid.
    participant_data = {"email": "", "cell_phone": "1234567890"}
    participant = Participant(**participant_data)
    assert participant.email == ""
    assert participant.cell_phone == participant_data["cell_phone"]

# Example of how to test model_dump and model_validate if needed, though often covered by usage
def test_participant_serialization_deserialization():
    participant_data = {"email": "serialize@example.com", "cell_phone": "1122334455"}
    participant = Participant(**participant_data)

    dumped_data = participant.model_dump()
    assert dumped_data["email"] == participant_data["email"]
    assert dumped_data["cell_phone"] == participant_data["cell_phone"]

    # Re-create from dumped data
    new_participant = Participant.model_validate(dumped_data)
    assert new_participant.email == participant_data["email"]
    assert new_participant.cell_phone == participant_data["cell_phone"]
    assert new_participant == participant
