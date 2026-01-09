import pytest

from chargehub.discovery.infrastructure.repositories.charging_station_repository import ChargingStationRepository
from chargehub.discovery.domain.aggregates.charging_station import ChargingStationAggregate
from chargehub.malfunction.application.malfunction_service import MalfunctionService
from chargehub.malfunction.infrastructure.repositories.report_repository import ReportRepositoryImpl

def test_report_text_validation():
    charging_repo = ChargingStationRepository([ChargingStationAggregate(station_id=1, postal_code="10115", latitude=52.52, longitude=13.40, available=True)])
    report_repo = ReportRepositoryImpl()
    service = MalfunctionService(report_repository=report_repo, charging_station_repository=charging_repo, threshold=5)

    with pytest.raises(ValueError):
        service.file_malfunction_report(1, "")

    with pytest.raises(ValueError):
        service.file_malfunction_report(1, "x" * 201)

def test_threshold_marks_station_unavailable():
    charging_repo = ChargingStationRepository([ChargingStationAggregate(station_id=1, postal_code="10115", latitude=52.52, longitude=13.40, available=True)])
    report_repo = ReportRepositoryImpl()
    service = MalfunctionService(report_repository=report_repo, charging_station_repository=charging_repo, threshold=5)

    # File 4 reports
    report_ids = []
    for i in range(4):
        service.file_malfunction_report(1, f"report {i}")
        # Identify the filed report ID to approve it
        # Since file_malfunction_report doesn't return ID anymore, we grab pending
        pending = report_repo.get_pending_reports()
        report_ids.append(pending[-1].id)
        service.approve_report(pending[-1].id)

    # 4 reports approved. Station should still be available (Threshold 5)
    station = charging_repo.get_all()[0]
    assert station.available is True

    # File 5th report
    service.file_malfunction_report(1, "report 4")
    pending = report_repo.get_pending_reports()
    
    # Approve 5th report -> Trigger threshold
    events = service.approve_report(pending[-1].id)
    
    assert any(e.__class__.__name__ == "MalfunctionReportThresholdReachedEvent" for e in events)
    assert any(getattr(e, "status", None) == "UNAVAILABLE" for e in events if e.__class__.__name__ == "StationStatusChangedEvent")

    station = charging_repo.get_all()[0]
    assert station.available is False

def test_repair_completed_restores_station():
    charging_repo = ChargingStationRepository([ChargingStationAggregate(station_id=1, postal_code="10115", latitude=52.52, longitude=13.40, available=False)])
    report_repo = ReportRepositoryImpl()
    service = MalfunctionService(report_repository=report_repo, charging_station_repository=charging_repo, threshold=5)

    # File reports to match threshold so repair is allowed
    for i in range(5):
         service.file_malfunction_report(1, f"Report {i}")
         pending = report_repo.get_pending_reports()
         service.approve_report(pending[-1].id)

    events = service.mark_repair_completed(1)
    assert any(e.__class__.__name__ == "RepairCompletedEvent" for e in events)
    assert any(e.__class__.__name__ == "StationRestoredEvent" for e in events)
    station = charging_repo.get_all()[0]
    assert station.available is True
    # Ensure reports are cleared
    assert report_repo.count_reports(1) == 0

def test_duplicate_report_raises_error():
    charging_repo = ChargingStationRepository([ChargingStationAggregate(station_id=1, postal_code="10115", latitude=52.52, longitude=13.40, available=True)])
    report_repo = ReportRepositoryImpl()
    service = MalfunctionService(report_repository=report_repo, charging_station_repository=charging_repo, threshold=5)

    service.file_malfunction_report(1, "Broken screen")
    
    # Even pending reports should block duplicates
    with pytest.raises(ValueError, match="Duplicate report content"):
        service.file_malfunction_report(1, "Broken screen")

def test_repair_fails_below_threshold():
    charging_repo = ChargingStationRepository([ChargingStationAggregate(station_id=1, postal_code="10115", latitude=52.52, longitude=13.40, available=False)])
    report_repo = ReportRepositoryImpl()
    service = MalfunctionService(report_repository=report_repo, charging_station_repository=charging_repo, threshold=5)

    # Only 1 report
    service.file_malfunction_report(1, "One report")
    pending = report_repo.get_pending_reports()
    service.approve_report(pending[-1].id)

    with pytest.raises(ValueError, match="Cannot repair"):
        service.mark_repair_completed(1)

