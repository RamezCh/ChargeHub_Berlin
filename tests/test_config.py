import pytest
from pathlib import Path
from chargehub.config import ChargeHubConfig

def test_chargehub_config_paths():
    """Test that paths are correctly resolved relative to the project root."""
    assert isinstance(ChargeHubConfig._PROJECT_ROOT, Path)
    assert isinstance(ChargeHubConfig.DATA_PATH, Path)
    assert isinstance(ChargeHubConfig.GEOJSON_PATH, Path)
    
    # Check if they point to the expected filenames
    assert ChargeHubConfig.DATA_PATH.name == "Ladesaeulenregister.csv"
    assert ChargeHubConfig.GEOJSON_PATH.name == "berlin_plz.geojson"

def test_chargehub_config_map_defaults():
    """Test map default values."""
    assert ChargeHubConfig.MAP_CENTER_LAT == 52.5200
    assert ChargeHubConfig.MAP_CENTER_LNG == 13.4050
    assert ChargeHubConfig.MAP_ZOOM_DEFAULT == 11

def test_chargehub_config_business_logic():
    """Test business logic constants."""
    assert ChargeHubConfig.REPAIR_THRESHOLD == 5
