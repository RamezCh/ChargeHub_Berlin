import streamlit as st
import folium
from streamlit_folium import st_folium
from chargehub.config import ChargeHubConfig
from chargehub.discovery.application.charging_station_service import ChargingStationService
from chargehub.malfunction.application.malfunction_service import MalfunctionService
from chargehub.discovery.infrastructure.repositories.charging_station_csv_repository import ChargingStationCSVRepository

class ChargingStationView:
    def __init__(self, 
                 discovery_service: ChargingStationService, 
                 malfunction_service: MalfunctionService,
                 charging_repo: ChargingStationCSVRepository,
                 config: ChargeHubConfig,
                 geojson_data: dict = None):
        self.discovery_service = discovery_service
        self.malfunction_service = malfunction_service
        self.charging_repo = charging_repo
        self.config = config
        self.geojson_data = geojson_data

    def render(self):
        st.header("🔌 Find a Charging Station")
        
        # Search
        postal_code = st.text_input("Search by Postal Code (PLZ)", placeholder="e.g. 10437")
        
        # Get stations
        if postal_code:
            try:
                stations, _ = self.discovery_service.locate_charging_stations(postal_code.strip())
                if not stations:
                    st.warning("No stations found.")
                else:
                    st.success(f"Found {len(stations)} stations.")
            except Exception as e:
                st.error(f"Error: {e}")
                stations = []
        else:
            stations = self.charging_repo.get_all()[:50]
            st.info(f"Showing {len(stations)} stations. Enter a PLZ to filter.")

        # Build and render map
        m = self._build_map(stations, postal_code.strip() if postal_code else None)
        st_folium(m, width="100%", height=500)
        
        st.divider()
        
        st.divider()
        
        # Report form with modern styling
        st.subheader("🛠️ Report a Malfunction")
        st.caption("Help us keep Berlin charging! Reports require admin approval before affecting station status.")
        
        with st.container(border=True):
            st.markdown("**Submit a New Report**")
            with st.form("report_form", border=False):
                col1, col2 = st.columns([1, 3])
                with col1:
                    station_id = st.number_input("Station ID", min_value=1, step=1)
                with col2:
                    description = st.text_input("Issue Description", max_chars=100, placeholder="e.g., Screen broken, Connector damaged")
                
                submitted = st.form_submit_button("Submit Report", type="primary", use_container_width=True)
                
                if submitted:
                    if description.strip():
                        try:
                            self.malfunction_service.file_malfunction_report(station_id, description)
                            st.success(f"Report submitted for Station **{station_id}**. Status: *Pending Approval*.")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                    else:
                        st.warning("Please describe the issue before submitting.")

    def _build_map(self, stations, highlight_plz=None):
        m = folium.Map(
            location=[self.config.MAP_CENTER_LAT, self.config.MAP_CENTER_LNG], 
            zoom_start=self.config.MAP_ZOOM_DEFAULT
        )
        
        # District highlighting
        if highlight_plz and self.geojson_data:
            folium.GeoJson(
                self.geojson_data,
                style_function=lambda f: {
                    "fillColor": "#ff7800" if f["properties"]["plz_code"] == highlight_plz else "transparent",
                    "color": "#ff7800" if f["properties"]["plz_code"] == highlight_plz else "transparent",
                    "weight": 2,
                    "fillOpacity": 0.4 if f["properties"]["plz_code"] == highlight_plz else 0.0,
                },
                name="District"
            ).add_to(m)
        
        # Add markers
        for s in stations:
            color = "green" if s.available else "red"
            status = "Available" if s.available else "Malfunctioning"
            
            folium.Marker(
                location=[s.latitude, s.longitude],
                popup=f"<b>Station {s.station_id}</b><br>{s.operator}<br>{s.address}<br>Status: {status}",
                tooltip=f"Station {s.station_id}",
                icon=folium.Icon(color=color, icon="bolt", prefix="fa")
            ).add_to(m)

        # Fit bounds
        if stations:
            lats = [s.latitude for s in stations]
            lons = [s.longitude for s in stations]
            m.fit_bounds([[min(lats), min(lons)], [max(lats), max(lons)]])
            
        return m
