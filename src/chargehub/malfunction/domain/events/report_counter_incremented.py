from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class ReportCounterIncrementedEvent:
    station_id: int
    current_count: int
