from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class PostalCode:
    """Value Object for Berlin postal codes.

    Business Rules (from diagrams):
    - Numeric only
    - Exactly 5 digits
    - Begins with 10, 12 or 13
    """
    value: str

    def __post_init__(self) -> None:
        if not self.value.isdigit():
            raise ValueError("Postal code must be numeric")
        if len(self.value) != 5:
            raise ValueError("Postal code must have exactly 5 digits")
        if not self.value.startswith(("10", "12", "13")):
            raise ValueError("Postal code must start with 10, 12 or 13")
