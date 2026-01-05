import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from pathlib import Path

from chargehub.discovery.infrastructure.repositories.charging_station_csv_repository import ChargingStationCSVRepository
from chargehub.discovery.domain.value_objects.postal_code import PostalCode

@pytest.fixture
def mock_csv_data():
    return pd.DataFrame({
        "Postleitzahl": ["10115", "10589", "12345", "99999"],
        "Breitengrad": ["52.5", "invalid", "52.4", ""],
        "Längengrad": ["13.4", "invalid", "13.3", ""],
        "Betreiber": ["Op1", "Robert Bosch", "Op2", "Op3"],
        "Straße": ["Street1", "Street2", "Street3", "Street4"],
        "Hausnummer": ["1", "2", "3", "4"]
    })

@patch("pandas.read_csv")
def test_load_stations(mock_read_csv, mock_csv_data):
    """Test loading stations with valid and invalid data."""
    mock_read_csv.return_value = mock_csv_data
    
    # Create repository
    repo = ChargingStationCSVRepository(Path("dummy.csv"))
    
    # Verify load
    stations = repo.get_all()
    assert len(stations) == 2 # 99999 skipped (no coords), 10589 skipped (Robert Bosch + invalid coords), 10115 kept, 12345 kept
    
    # Verify specific station details
    s1 = next(s for s in stations if s.postal_code == "10115")
    assert s1.latitude == 52.5
    assert s1.longitude == 13.4
    
    # Verify 10589 Logic (Robert Bosch logic from code)
    # The code says if 10589 and Robert Bosch is NOT in operator, apply default coords.
    # Here Robert Bosch IS in operator, but coords are invalid.
    # Wait, the code says:
    # if postal_code == "10589" and "Robert Bosch" not in str(row.get("Betreiber")):
    #      if not lat_str or not lon_str or float(lat_str) < 50: override
    # So if it IS Robert Bosch, it does NOT override.
    # If coords are invalid, it skips.
    # In my mock data: 10589, Robert Bosch, invalid coords -> Should be skipped?
    # Let's check the code:
    # 10589 check passes (it is Robert Bosch, so the 'if' condition is false)
    # Then it hits 'if not lat_str or not lon_str' -> 'invalid' is not empty, but float conversion fails later.
    # try: float('invalid') -> validation error -> continue.
    # So actually my expectation of 3 might be wrong if 10589 is skipped.
    
    # Let's adjust expectation based on code analysis:
    # 10115: Valid.
    # 10589: "Robert Bosch" is IN operator. So the special fix block is SKIPPED. Coords are "invalid". float() fails. SKIPPED.
    # 12345: Valid.
    # 99999: Coords empty. SKIPPED.
    # So we expect 2 stations.
    
    assert len(stations) == 2 

@patch("pandas.read_csv")
def test_load_stations_10589_fix(mock_read_csv):
    """Test the specific 10589 fix logic."""
    data = pd.DataFrame({
        "Postleitzahl": ["10589"],
        "Breitengrad": [""],
        "Längengrad": [""],
        "Betreiber": ["Other Op"], # NOT Robert Bosch
        "Straße": ["S"], 
        "Hausnummer": ["1"]
    })
    mock_read_csv.return_value = data
    
    repo = ChargingStationCSVRepository(Path("dummy.csv"))
    stations = repo.get_all()
    
    assert len(stations) == 1
    s = stations[0]
    assert s.postal_code == "10589"
    assert s.latitude == 52.5263
    assert s.longitude == 13.3039

@patch("pandas.read_csv")
def test_locate_charging_stations(mock_read_csv, mock_csv_data):
    mock_read_csv.return_value = mock_csv_data
    repo = ChargingStationCSVRepository(Path("dummy.csv"))
    
    # 10115 matches one station
    results = repo.locate_charging_stations(PostalCode("10115"))
    assert len(results) == 1
    assert results[0].postal_code == "10115"
    
    # 10999 matches none (but is valid format starting with 10)
    results = repo.locate_charging_stations(PostalCode("10999"))
    assert len(results) == 0

@patch("pandas.read_csv")
def test_update_station_status(mock_read_csv, mock_csv_data):
    mock_read_csv.return_value = mock_csv_data
    repo = ChargingStationCSVRepository(Path("dummy.csv"))
    
    # Get a station ID (index from dataframe)
    # DataFrame indices: 0, 1, 2, 3
    # 10115 is at index 0.
    
    repo.update_station_status(0, False)
    
    stations = repo.get_all()
    s0 = next(s for s in stations if s.station_id == 0)
    assert s0.available is False
    
    # Test error
    with pytest.raises(KeyError):
        repo.update_station_status(999, False)
