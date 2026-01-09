from abc import ABC, abstractmethod
from typing import List
from uuid import UUID
from chargehub.malfunction.domain.aggregates.malfunction_report import ReportStatus

class ReportRepository(ABC):
    """
    Domain Repository Interface for Malfunction Reports.
    """

    @abstractmethod
    def save_report(self, station_id: int, report_text: str) -> UUID:
        pass

    @abstractmethod
    def update_status(self, report_id: UUID, status: ReportStatus) -> None:
        pass

    @abstractmethod
    def count_reports(self, station_id: int) -> int:
        pass

    @abstractmethod
    def has_report(self, station_id: int, report_text: str) -> bool:
        pass

    @abstractmethod
    def clear_reports(self, station_id: int) -> None:
        pass
