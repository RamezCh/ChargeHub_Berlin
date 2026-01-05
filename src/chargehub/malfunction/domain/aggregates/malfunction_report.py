from __future__ import annotations

from dataclasses import dataclass
from chargehub.malfunction.domain.value_objects.report_text import ReportText

@dataclass()
class MalfunctionReportAggregate:
    """Aggregate Root representing a malfunction report."""
    station_id: int
    report: ReportText
    acknowledged: bool = False
