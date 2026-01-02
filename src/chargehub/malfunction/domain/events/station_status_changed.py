from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class StationStatusChangedEvent:
    station_id: int
    status: str  # 'UNAVAILABLE' or 'AVAILABLE'
