from pathlib import Path

class ChargeHubConfig:
    # Paths
    # Assumes run from project root. 
    # Adjust relative path logic if needed, but __file__ based is safer if config is in src/chargehub
    _PROJECT_ROOT = Path(__file__).parent.parent.parent
    DATA_PATH = _PROJECT_ROOT / "data" / "Ladesaeulenregister.csv"
    GEOJSON_PATH = _PROJECT_ROOT / "data" / "berlin_plz.geojson"

    # Map Defaults (Berlin)
    MAP_CENTER_LAT = 52.5200
    MAP_CENTER_LNG = 13.4050
    MAP_ZOOM_DEFAULT = 11
    
    # Business Logic
    REPAIR_THRESHOLD = 5
