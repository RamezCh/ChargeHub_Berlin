from __future__ import annotations

from dataclasses import dataclass

@dataclass()
class ChargingStationAggregate:
    """Aggregate Root representing a charging station.

    Minimal fields to support the two core use cases:
    - postal_code
    - availability status
    """
    station_id: int
    postal_code: str
    latitude: float
    longitude: float
    available: bool = True
    operator: str | None = None
    address: str | None = None
