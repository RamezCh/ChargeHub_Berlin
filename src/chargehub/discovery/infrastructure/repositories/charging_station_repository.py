from __future__ import annotations

from typing import Iterable, List
from chargehub.discovery.domain.aggregates.charging_station import ChargingStationAggregate
from chargehub.discovery.domain.value_objects.postal_code import PostalCode
from chargehub.discovery.domain.interfaces.charging_station_repository import ChargingStationRepository

class ChargingStationRepository(ChargingStationRepository):
    """InMemory repository (as required by ASE guideline)."""

    def __init__(self, stations: Iterable[ChargingStationAggregate] | None = None) -> None:
        self._stations: List[ChargingStationAggregate] = list(stations or [])

    def add(self, station: ChargingStationAggregate) -> None:
        self._stations.append(station)

    def locate_charging_stations(self, postal_code: PostalCode) -> List[ChargingStationAggregate]:
        """Return stations for a PLZ, filtered to AVAILABLE only (real-time filter)."""
        return [
            s for s in self._stations
            if s.postal_code == postal_code.value and s.available
        ]

    def update_station_status(self, station_id: int, status: bool) -> None:
        for s in self._stations:
            if s.station_id == station_id:
                s.available = status
                return
        raise KeyError(f"Station {station_id} not found")

    def get_all(self) -> List[ChargingStationAggregate]:
        return list(self._stations)
