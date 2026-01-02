from __future__ import annotations
from dataclasses import dataclass
from typing import Sequence

@dataclass(frozen=True)
class StationsFoundEvent:
    stations: Sequence[int]  # station_ids
