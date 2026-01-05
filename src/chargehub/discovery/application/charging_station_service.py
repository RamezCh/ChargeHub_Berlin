from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence

from chargehub.discovery.application.dtos.charging_station_dto import ChargingStationDTO
from chargehub.discovery.application.dtos.empty_charging_stations_dto import EmptyChargingStationsDTO
from chargehub.discovery.domain.events.station_search_initiated import StationSearchInitiatedEvent
from chargehub.discovery.domain.events.postal_code_validated import PostalCodeValidatedEvent
from chargehub.discovery.domain.events.station_failed_event import StationFailedEvent
from chargehub.discovery.domain.events.stations_found import StationsFoundEvent
from chargehub.discovery.domain.events.no_stations_found import NoStationsFoundEvent
from chargehub.discovery.domain.value_objects.postal_code import PostalCode
from chargehub.discovery.infrastructure.repositories.charging_station_repository import ChargingStationRepository

@dataclass()
class ChargingStationService:
    """Application Service implementing the 'Search Charging Stations' use case."""
    repository: ChargingStationRepository

    def locate_charging_stations(self, postal_code: str) -> tuple[List[ChargingStationDTO] | EmptyChargingStationsDTO, Sequence[object]]:
        events: list[object] = [StationSearchInitiatedEvent(postal_code=postal_code)]
        try:
            pc = PostalCode(postal_code)
            events.append(PostalCodeValidatedEvent(postal_code=pc.value))
        except ValueError:
            events.append(StationFailedEvent(reason="Invalid Format"))
            raise

        stations = self.repository.locate_charging_stations(pc)
        if not stations:
            events.append(NoStationsFoundEvent(postal_code=pc.value))
            return EmptyChargingStationsDTO(), events

        events.append(StationsFoundEvent(stations=[s.station_id for s in stations]))
        dtos = [ChargingStationDTO(
            station_id=s.station_id,
            postal_code=s.postal_code,
            latitude=s.latitude,
            longitude=s.longitude,
            available=s.available,
            operator=s.operator,
            address=s.address,
        ) for s in stations]
        return dtos, events
