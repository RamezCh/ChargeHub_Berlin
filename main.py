from __future__ import annotations
import sys
from pathlib import Path

# Add src to sys.path
sys.path.append(str(Path(__file__).parent / "src"))

import streamlit as st
import requests

from chargehub.config import ChargeHubConfig
from chargehub.discovery.application.charging_station_service import ChargingStationService
from chargehub.discovery.infrastructure.repositories.charging_station_csv_repository import ChargingStationCSVRepository
from chargehub.malfunction.application.malfunction_service import MalfunctionService
from chargehub.malfunction.infrastructure.repositories.report_repository import ReportRepository

# Import Presentation Layer
from chargehub.presentation.user_view import UserView
from chargehub.presentation.admin_view import AdminView

# ------------------------------------------------------------
# Configuration & Setup
# ------------------------------------------------------------
st.set_page_config(
    page_title="ChargeHub Berlin",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize Services (Singleton-ish pattern for Streamlit)
@st.cache_resource
def get_container():
    config = ChargeHubConfig()
    
    charging_repo = ChargingStationCSVRepository(config.DATA_PATH)
    report_repo = ReportRepository()
    
    discovery_service = ChargingStationService(repository=charging_repo)
    malfunction_service = MalfunctionService(
        report_repository=report_repo,
        charging_station_repository=charging_repo,
        threshold=config.REPAIR_THRESHOLD,
    )
    return config, charging_repo, discovery_service, malfunction_service

config, charging_repo, discovery_service, malfunction_service = get_container()

# Load GeoJSON (Cached)
@st.cache_data
def get_berlin_geojson(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception:
        return None

geojson_data = get_berlin_geojson(config.GEOJSON_URL)

# ------------------------------------------------------------
# Views Initialization
# ------------------------------------------------------------
# Dependency Injection for Views
user_view = UserView(
    discovery_service=discovery_service,
    malfunction_service=malfunction_service,
    charging_repo=charging_repo,
    config=config,
    geojson_data=geojson_data
)

admin_view = AdminView(
    malfunction_service=malfunction_service,
    charging_repo=charging_repo,
    config=config
)

# ------------------------------------------------------------
# Main Routine (Router)
# ------------------------------------------------------------
def sidebar_role_switcher():
    with st.sidebar:
        st.title("⚡ ChargeHub")
        st.markdown("**Berlin Edition**")
        st.divider()
        role = st.radio("Select Role", ["USER", "ADMIN"], index=0)
        st.divider()
        st.caption("v1.3.0 • SOLID Architecture")
    return role

def main():
    role = sidebar_role_switcher()
    
    if role == "USER":
        user_view.render()
    else:
        admin_view.render()

if __name__ == "__main__":
    main()
