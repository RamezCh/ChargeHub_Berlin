from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class ChargingStationDTO:
    station_id: int
    postal_code: str
    latitude: float
    longitude: float
    available: bool
    operator: str | None = None
    address: str | None = None
