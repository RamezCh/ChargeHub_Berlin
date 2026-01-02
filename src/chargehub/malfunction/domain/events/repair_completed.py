from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class RepairCompletedEvent:
    station_id: int
    action: str = "Fixed"
