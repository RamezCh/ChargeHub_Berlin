from __future__ import annotations

from dataclasses import dataclass
from chargehub.malfunction.domain.value_objects.report_text import ReportText

from enum import Enum, auto

class ReportStatus(Enum):
    PENDING = auto()
    APPROVED = auto()
    REJECTED = auto()

@dataclass()
class MalfunctionReportAggregate:
    """Aggregate Root representing a malfunction report."""
    station_id: int
    report: ReportText
    status: ReportStatus = ReportStatus.PENDING
    acknowledged: bool = False
