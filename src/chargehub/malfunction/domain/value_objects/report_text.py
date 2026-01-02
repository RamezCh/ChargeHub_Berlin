from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class ReportText:
    """Value Object for malfunction report content.

    Business Rules:
    - Not empty
    - Max 200 characters
    """
    value: str

    def __post_init__(self) -> None:
        if self.value is None or self.value.strip() == "":
            raise ValueError("Report must not be empty")
        if len(self.value) > 200:
            raise ValueError("Report must be <= 200 characters")
