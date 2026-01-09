from abc import ABC, abstractmethod
from typing import List
from chargehub.discovery.domain.aggregates.charging_station import ChargingStationAggregate
from chargehub.discovery.domain.value_objects.postal_code import PostalCode

class ChargingStationRepository(ABC):
    """
    Domain Repository Interface.
    Follows Dependency Inversion Principle: High-level modules (Domain/Service) 
    depend on this abstraction, not concrete implementations (CSV/DB).
    """

    @abstractmethod
    def locate_charging_stations(self, postal_code: PostalCode) -> List[ChargingStationAggregate]:
        pass

    @abstractmethod
    def update_station_status(self, station_id: int, status: bool) -> None:
        pass

    @abstractmethod
    def get_all(self) -> List[ChargingStationAggregate]:
        pass
