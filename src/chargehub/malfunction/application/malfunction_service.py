from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from chargehub.discovery.infrastructure.repositories.charging_station_repository import ChargingStationRepository
from chargehub.malfunction.domain.value_objects.report_text import ReportText
from chargehub.malfunction.infrastructure.repositories.report_repository import ReportRepository
from chargehub.malfunction.domain.events.malfunction_report_filed import MalfunctionReportFiledEvent
from chargehub.malfunction.domain.events.administrator_notified import AdministratorNotifiedEvent
from chargehub.malfunction.domain.events.report_counter_incremented import ReportCounterIncrementedEvent
from chargehub.malfunction.domain.events.malfunction_report_threshold_reached import MalfunctionReportThresholdReachedEvent
from chargehub.malfunction.domain.events.station_status_changed import StationStatusChangedEvent
from chargehub.malfunction.domain.events.repair_completed import RepairCompletedEvent

@dataclass()
class MalfunctionService:
    """Application Service implementing 'Report Malfunctioning Stations'."""

    report_repository: ReportRepository
    charging_station_repository: ChargingStationRepository
    threshold: int = 5

    def file_malfunction_report(self, station_id: int, report: str) -> Sequence[object]:
        events: list[object] = []
        rt = ReportText(report)  # validates itself

        events.append(MalfunctionReportFiledEvent(station_id=station_id, report=rt.value))
        events.append(AdministratorNotifiedEvent(station_id=station_id))

        current_count = self.report_repository.save_report(station_id=station_id, report_text=rt.value)
        events.append(ReportCounterIncrementedEvent(station_id=station_id, current_count=current_count))

        if current_count >= self.threshold:
            events.append(MalfunctionReportThresholdReachedEvent(
                station_id=station_id, threshold=self.threshold, current_count=current_count
            ))
            # Update station status to UNAVAILABLE
            self.charging_station_repository.update_station_status(station_id=station_id, status=False)
            events.append(StationStatusChangedEvent(station_id=station_id, status="UNAVAILABLE"))

        return events

    def mark_repair_completed(self, station_id: int) -> Sequence[object]:
        # Repair completed -> station restored AVAILABLE
        self.charging_station_repository.update_station_status(station_id=station_id, status=True)
        return [
            RepairCompletedEvent(station_id=station_id),
            StationStatusChangedEvent(station_id=station_id, status="AVAILABLE"),
        ]
