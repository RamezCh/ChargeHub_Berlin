from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class MalfunctionReportFiledEvent:
    station_id: int
    report: str
