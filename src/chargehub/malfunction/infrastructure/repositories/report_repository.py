from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

@dataclass()
class StoredReport:
    station_id: int
    report_text: str

class ReportRepository:
    """InMemory repository for malfunction reports."""

    def __init__(self) -> None:
        self._reports: List[StoredReport] = []
        self._count_by_station: Dict[int, int] = {}

    def save_report(self, station_id: int, report_text: str) -> int:
        self._reports.append(StoredReport(station_id=station_id, report_text=report_text))
        self._count_by_station[station_id] = self._count_by_station.get(station_id, 0) + 1
        return self._count_by_station[station_id]

    def count_reports(self, station_id: int) -> int:
        return self._count_by_station.get(station_id, 0)

    def all_reports(self) -> List[StoredReport]:
        return list(self._reports)

    def get_affected_station_ids(self) -> List[int]:
        return list(self._count_by_station.keys())

    def has_report(self, station_id: int, report_text: str) -> bool:
        return any(r.station_id == station_id and r.report_text == report_text for r in self._reports)

    def clear_reports(self, station_id: int) -> None:
        self._reports = [r for r in self._reports if r.station_id != station_id]
        if station_id in self._count_by_station:
            del self._count_by_station[station_id]
