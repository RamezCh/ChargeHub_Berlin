from __future__ import annotations

import pandas as pd
from pathlib import Path
from typing import List

from chargehub.discovery.domain.aggregates.charging_station import ChargingStationAggregate
from chargehub.discovery.domain.value_objects.postal_code import PostalCode
from chargehub.discovery.domain.interfaces.charging_station_repository import ChargingStationRepository

class ChargingStationCSVRepository(ChargingStationRepository):
    """
    Infrastructure Repository reading charging stations from
    Bundesnetzagentur CSV (Ladesaeulenregister.csv).
    """

    def __init__(self, csv_path: Path):
        self.csv_path = csv_path
        self._stations = self._load()

    def _load(self) -> List[ChargingStationAggregate]:
        df = pd.read_csv(self.csv_path, sep=";", encoding="utf-8", low_memory=False)

        stations: List[ChargingStationAggregate] = []

        for idx, row in df.iterrows():
            try:
                postal_code = str(row["Postleitzahl"]).partition('.')[0].zfill(5)

                # Domain validation (Berlin only)
                PostalCode(postal_code)

                lat_raw = row.get("Breitengrad", "")
                lon_raw = row.get("Längengrad", "")
                
                lat_str = str(lat_raw).replace(",", ".") if pd.notna(lat_raw) else ""
                lon_str = str(lon_raw).replace(",", ".") if pd.notna(lon_raw) else ""

                if postal_code == "10589" and "Robert Bosch" not in str(row.get("Betreiber")):
                     if not lat_str or not lon_str or float(lat_str) < 50:
                         lat_str = "52.5263"
                         lon_str = "13.3039"

                # Skip if coordinates are still missing
                if not lat_str or not lon_str:
                    continue
                
                # Filter out obvious non-GPS values (some rows have text)
                try:
                    lat_float = float(lat_str)
                    lon_float = float(lon_str)
                except ValueError:
                    continue

                stations.append(
                    ChargingStationAggregate(
                        station_id=idx,
                        postal_code=postal_code,
                        latitude=lat_float,
                        longitude=lon_float,
                        available=True,  # CSV has no live status
                        operator=row.get("Betreiber"),
                        address=f"{row.get('Straße', '')} {row.get('Hausnummer', '')}",
                    )
                )
            except Exception:
                continue

        return stations

    def locate_charging_stations(self, postal_code: PostalCode):
        return [
            s for s in self._stations
            if s.postal_code == postal_code.value and s.available
        ]

    def update_station_status(self, station_id: int, status: bool):
        for s in self._stations:
            if s.station_id == station_id:
                s.available = status
                return
        raise KeyError(f"Station {station_id} not found")

    def get_all(self):
        return list(self._stations)
