from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class NoStationsFoundEvent:
    postal_code: str
