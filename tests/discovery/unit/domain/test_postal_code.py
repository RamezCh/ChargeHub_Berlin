import pytest
from chargehub.discovery.domain.value_objects.postal_code import PostalCode

def test_valid_postal_code():
    pc = PostalCode("10115")
    assert pc.value == "10115"

@pytest.mark.parametrize("value", ["10A15", "1011", "99123", "ABCDE", ""])
def test_invalid_postal_code(value):
    with pytest.raises(ValueError):
        PostalCode(value)
