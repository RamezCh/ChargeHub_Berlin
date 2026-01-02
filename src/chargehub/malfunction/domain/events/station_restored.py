from dataclasses import dataclass

@dataclass(frozen=True)
class StationRestoredEvent:
    station_id: int
    status: str = "AVAILABLE"
