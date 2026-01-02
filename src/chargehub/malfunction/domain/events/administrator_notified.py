from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class AdministratorNotifiedEvent:
    station_id: int
