from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from chargehub.discovery.domain.interfaces.charging_station_repository import ChargingStationRepository
from chargehub.malfunction.domain.value_objects.report_text import ReportText
from chargehub.malfunction.domain.interfaces.report_repository import ReportRepository
from chargehub.malfunction.domain.events.malfunction_report_filed import MalfunctionReportFiledEvent
from chargehub.malfunction.domain.events.administrator_notified import AdministratorNotifiedEvent
from chargehub.malfunction.domain.events.report_counter_incremented import ReportCounterIncrementedEvent
from chargehub.malfunction.domain.events.malfunction_report_threshold_reached import MalfunctionReportThresholdReachedEvent
from chargehub.malfunction.domain.events.station_status_changed import StationStatusChangedEvent
from chargehub.malfunction.domain.events.repair_completed import RepairCompletedEvent
from chargehub.malfunction.domain.events.station_restored import StationRestoredEvent

@dataclass()
class MalfunctionService:
    """Application Service implementing 'Report Malfunctioning Stations'."""

    report_repository: ReportRepository
    charging_station_repository: ChargingStationRepository
    threshold: int = 5

    def file_malfunction_report(self, station_id: int, report: str) -> Sequence[object]:
        events: list[object] = []
        rt = ReportText(report)  # validates itself

        if self.report_repository.has_report(station_id, rt.value):
            raise ValueError("Duplicate report content for this station.")

        # Save report with PENDING status. NO counting increment yet.
        _ = self.report_repository.save_report(station_id=station_id, report_text=rt.value)
        
        events.append(MalfunctionReportFiledEvent(station_id=station_id, report=rt.value))
        events.append(AdministratorNotifiedEvent(station_id=station_id))

        return events

    def approve_report(self, report_id: str) -> Sequence[object]:
        from chargehub.malfunction.domain.aggregates.malfunction_report import ReportStatus
        from uuid import UUID
        
        if isinstance(report_id, str):
            report_id = UUID(report_id)

        # 1. Update status to APPROVED
        self.report_repository.update_status(report_id, ReportStatus.APPROVED)
        
        # 2. Get report details to find station_id
        # In a real event sourced system we'd get the aggregate. Here we rely on Repo.
        all_reports = self.report_repository.all_reports()
        report = next((r for r in all_reports if r.id == report_id), None)
        
        if not report:
            raise ValueError("Report not found")
        
        station_id = report.station_id
        current_count = self.report_repository.count_reports(station_id)
        
        events: list[object] = []
        events.append(ReportCounterIncrementedEvent(station_id=station_id, current_count=current_count))
        
        # 3. Check Threshold
        if current_count >= self.threshold:
            events.append(MalfunctionReportThresholdReachedEvent(
                station_id=station_id, threshold=self.threshold, current_count=current_count
            ))
            # Update station status to UNAVAILABLE
            self.charging_station_repository.update_station_status(station_id=station_id, status=False)
            events.append(StationStatusChangedEvent(station_id=station_id, status="UNAVAILABLE"))
            
        return events

    def reject_report(self, report_id: str) -> Sequence[object]:
        from chargehub.malfunction.domain.aggregates.malfunction_report import ReportStatus
        from uuid import UUID
        
        if isinstance(report_id, str):
            report_id = UUID(report_id)
            
        self.report_repository.update_status(report_id, ReportStatus.REJECTED)
        return []

    def mark_repair_completed(self, station_id: int) -> Sequence[object]:
        count = self.report_repository.count_reports(station_id)
        if count < self.threshold:
             raise ValueError(f"Cannot repair: Station has only {count} reports (Threshold: {self.threshold}).")

        # Repair completed -> station restored AVAILABLE
        self.charging_station_repository.update_station_status(station_id=station_id, status=True)
        self.report_repository.clear_reports(station_id)
        return [
            RepairCompletedEvent(station_id=station_id),
            StationRestoredEvent(station_id=station_id),
        ]
