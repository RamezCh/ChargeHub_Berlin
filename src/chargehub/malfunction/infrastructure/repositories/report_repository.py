from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

from uuid import uuid4, UUID
from chargehub.malfunction.domain.aggregates.malfunction_report import ReportStatus
from chargehub.malfunction.domain.interfaces.report_repository import ReportRepository

@dataclass()
class StoredReport:
    id: UUID
    station_id: int
    report_text: str
    status: ReportStatus

class ReportRepositoryImpl(ReportRepository):
    """InMemory repository for malfunction reports."""

    def __init__(self) -> None:
        self._reports: List[StoredReport] = []
        # Count cache now only tracks APPROVED reports
        self._count_by_station: Dict[int, int] = {}

    def save_report(self, station_id: int, report_text: str) -> UUID:
        report_id = uuid4()
        # Default status is PENDING
        self._reports.append(StoredReport(
            id=report_id, 
            station_id=station_id, 
            report_text=report_text,
            status=ReportStatus.PENDING
        ))
        # Do NOT increment count here anymore
        return report_id

    def update_status(self, report_id: UUID, status: ReportStatus) -> None:
        report = next((r for r in self._reports if r.id == report_id), None)
        if report:
            old_status = report.status
            report.status = status
            
            # Recalculate count for this station if status changes involves APPROVED
            if old_status != ReportStatus.APPROVED and status == ReportStatus.APPROVED:
                self._count_by_station[report.station_id] = self._count_by_station.get(report.station_id, 0) + 1
            elif old_status == ReportStatus.APPROVED and status != ReportStatus.APPROVED:
                 if report.station_id in self._count_by_station:
                     self._count_by_station[report.station_id] -= 1

    def count_reports(self, station_id: int) -> int:
        # Returns only APPROVED count
        return self._count_by_station.get(station_id, 0)

    def all_reports(self) -> List[StoredReport]:
        return list(self._reports)
    
    def get_pending_reports(self) -> List[StoredReport]:
        return [r for r in self._reports if r.status == ReportStatus.PENDING]

    def get_affected_station_ids(self) -> List[int]:
        # Only return stations with APPROVED reports > 0
        return [sid for sid, count in self._count_by_station.items() if count > 0]

    def has_report(self, station_id: int, report_text: str) -> bool:
        # Check against all reports regardless of status to prevent spam
        return any(r.station_id == station_id and r.report_text == report_text for r in self._reports)

    def clear_reports(self, station_id: int) -> None:
        # Archive or remove? For simplicity we remove them as per original spec, 
        # but in real world better to archive.
        self._reports = [r for r in self._reports if r.station_id != station_id]
        if station_id in self._count_by_station:
            del self._count_by_station[station_id]
