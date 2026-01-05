import pytest

from chargehub.discovery.application.charging_station_service import ChargingStationService
from chargehub.discovery.infrastructure.repositories.charging_station_repository import ChargingStationRepository
from chargehub.discovery.domain.aggregates.charging_station import ChargingStationAggregate

def test_search_returns_only_available_stations():
    stations = [
        ChargingStationAggregate(station_id=1, postal_code="10115", latitude=52.52, longitude=13.40, available=True),
        ChargingStationAggregate(station_id=2, postal_code="10115", latitude=52.52, longitude=13.40, available=False),
        ChargingStationAggregate(station_id=3, postal_code="12043", latitude=52.52, longitude=13.40, available=True),
    ]
    repo = ChargingStationRepository(stations)
    service = ChargingStationService(repository=repo)

    results, events = service.locate_charging_stations("10115")
    assert [r.station_id for r in results] == [1]
    # includes a "StationsFoundEvent"
    assert any(e.__class__.__name__ == "StationsFoundEvent" for e in events)

def test_search_invalid_postal_code_raises():
    repo = ChargingStationRepository([])
    service = ChargingStationService(repository=repo)
    with pytest.raises(ValueError):
        service.locate_charging_stations("ABCDE")

def test_search_no_stations_found_event():
    repo = ChargingStationRepository([ChargingStationAggregate(station_id=1, postal_code="10115", latitude=52.52, longitude=13.40, available=False)])
    service = ChargingStationService(repository=repo)
    from chargehub.discovery.application.dtos.empty_charging_stations_dto import EmptyChargingStationsDTO
    results, events = service.locate_charging_stations("10115")
    assert isinstance(results, EmptyChargingStationsDTO)
    assert any(e.__class__.__name__ == "NoStationsFoundEvent" for e in events)
