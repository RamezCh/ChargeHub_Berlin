from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class MalfunctionReportThresholdReachedEvent:
    station_id: int
    threshold: int
    current_count: int
