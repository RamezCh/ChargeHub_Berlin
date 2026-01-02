import pytest

from chargehub.discovery.infrastructure.repositories.charging_station_repository import ChargingStationRepository
from chargehub.discovery.domain.aggregates.charging_station import ChargingStationAggregate
from chargehub.malfunction.application.malfunction_service import MalfunctionService
from chargehub.malfunction.infrastructure.repositories.report_repository import ReportRepository

def test_report_text_validation():
    charging_repo = ChargingStationRepository([ChargingStationAggregate(1, "10115", True)])
    report_repo = ReportRepository()
    service = MalfunctionService(report_repository=report_repo, charging_station_repository=charging_repo, threshold=5)

    with pytest.raises(ValueError):
        service.file_malfunction_report(1, "")

    with pytest.raises(ValueError):
        service.file_malfunction_report(1, "x" * 201)

def test_threshold_marks_station_unavailable():
    charging_repo = ChargingStationRepository([ChargingStationAggregate(1, "10115", True)])
    report_repo = ReportRepository()
    service = MalfunctionService(report_repository=report_repo, charging_station_repository=charging_repo, threshold=5)

    for i in range(4):
        events = service.file_malfunction_report(1, f"report {i}")
        assert not any(e.__class__.__name__ == "StationStatusChangedEvent" for e in events)

    events = service.file_malfunction_report(1, "report 4")
    assert any(e.__class__.__name__ == "MalfunctionReportThresholdReachedEvent" for e in events)
    assert any(getattr(e, "status", None) == "UNAVAILABLE" for e in events if e.__class__.__name__ == "StationStatusChangedEvent")

    station = charging_repo.get_all()[0]
    assert station.available is False

def test_repair_completed_restores_station():
    charging_repo = ChargingStationRepository([ChargingStationAggregate(1, "10115", False)])
    report_repo = ReportRepository()
    service = MalfunctionService(report_repository=report_repo, charging_station_repository=charging_repo, threshold=5)

    events = service.mark_repair_completed(1)
    assert any(e.__class__.__name__ == "RepairCompletedEvent" for e in events)
    station = charging_repo.get_all()[0]
    assert station.available is True
