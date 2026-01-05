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
    assert len(stations) == 2
    
    # Verify specific station details
    s1 = next(s for s in stations if s.postal_code == "10115")
    assert s1.latitude == 52.5
    assert s1.longitude == 13.4
    
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
