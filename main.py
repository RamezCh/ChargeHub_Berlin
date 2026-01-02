from __future__ import annotations

import sys
from pathlib import Path
import pandas as pd

# Add src to sys.path
sys.path.append(str(Path(__file__).parent / "src"))

import streamlit as st
import folium
from streamlit_folium import st_folium
from dataclasses import asdict, is_dataclass

from chargehub.discovery.application.charging_station_service import (
    ChargingStationService,
)
from chargehub.discovery.infrastructure.repositories.charging_station_csv_repository import (
    ChargingStationCSVRepository,
)
from chargehub.malfunction.application.malfunction_service import (
    MalfunctionService,
)
from chargehub.malfunction.infrastructure.repositories.report_repository import (
    ReportRepository,
)

# ------------------------------------------------------------
# Configuration & Setup
# ------------------------------------------------------------
st.set_page_config(
    page_title="ChargeHub Berlin",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_PATH = Path(__file__).parent / "data" / "Ladesaeulenregister.csv"

# Initialize Services (Singleton-ish pattern for Streamlit)
@st.cache_resource
def get_services():
    charging_repo = ChargingStationCSVRepository(DATA_PATH)
    report_repo = ReportRepository()
    
    discovery_service = ChargingStationService(repository=charging_repo)
    malfunction_service = MalfunctionService(
        report_repository=report_repo,
        charging_station_repository=charging_repo,
        threshold=5,
    )
    return charging_repo, discovery_service, malfunction_service

charging_repo, discovery_service, malfunction_service = get_services()

# Load GeoJSON for Berlin Postal Codes (Cached)
@st.cache_data
def get_berlin_geojson():
    import requests
    url = "https://tsb-opendata.s3.eu-central-1.amazonaws.com/plz_berlin.geojson"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception:
        return None

geojson_data = get_berlin_geojson()

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------
def event_to_dict(event: object) -> dict:
    if is_dataclass(event):
        return {"event": event.__class__.__name__, **asdict(event)}
    return {"event": event.__class__.__name__}

# ------------------------------------------------------------
# UI Components
# ------------------------------------------------------------
def sidebar_role_switcher():
    with st.sidebar:
        st.title("⚡ ChargeHub")
        st.markdown("**Berlin Edition**")
        st.divider()
        role = st.radio("Select Role", ["USER", "ADMIN"], index=0)
        st.divider()
        st.caption("v1.2.0 • Map & Dashboard")
    return role

def render_map(stations, highlight_plz=None, selected_station_id=None):
    # Center on Berlin
    m = folium.Map(location=[52.5200, 13.4050], zoom_start=11)
    
    # District Highlighting
    if highlight_plz and geojson_data:
        folium.GeoJson(
            geojson_data,
            style_function=lambda feature: {
                "fillColor": "#ff7800" if feature["properties"]["plz"] == highlight_plz else "transparent",
                "color": "#ff7800" if feature["properties"]["plz"] == highlight_plz else "transparent",
                "weight": 2,
                "fillOpacity": 0.4 if feature["properties"]["plz"] == highlight_plz else 0.0,
            },
            name="District"
        ).add_to(m)
    
    for s in stations:
        # Color marker based on availability
        color = "green" if s.available else "red"
        status_text = "Available" if s.available else "Malfunctioning"
        
        # Show popup if selected
        is_selected = (s.station_id == selected_station_id)
        
        folium.Marker(
            location=[s.latitude, s.longitude],
            popup=folium.Popup(f"<b>ID: {s.station_id}</b><br>{s.operator}<br><i>{status_text}</i>", max_width=200, show=is_selected),
            tooltip=f"{s.address} (ID: {s.station_id})",
            icon=folium.Icon(color=color, icon="bolt", prefix="fa")
        ).add_to(m)

    # Auto-Zoom
    if stations:
        lats = [s.latitude for s in stations]
        lons = [s.longitude for s in stations]
        m.fit_bounds([[min(lats), min(lons)], [max(lats), max(lons)]])
        
    return m

# ------------------------------------------------------------
# USER VIEW
# ------------------------------------------------------------
def render_user_view():
    st.header("🔌 Find a Charging Station")
    st.markdown("Use the map below to locate available charging pillars in Berlin. Click a pin to view details or report issues.")
    
    col1, col2 = st.columns([2, 1], gap="medium")
    
    with col1:
        postal_code = st.text_input("Search by Postal Code (PLZ)", placeholder="e.g. 10437")
        
        stations = []
        if postal_code:
            try:
                stations, _ = discovery_service.search_by_postal_code(postal_code.strip())
                if not stations:
                    st.warning("No stations found for this zip code.")
                else:
                    st.success(f"Found {len(stations)} stations in district {postal_code}.")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            all_stations = charging_repo.get_all()
            stations = all_stations[:50] # Limit for view
            st.info(f"Showing {len(stations)} random stations. Enter a PLZ to filter.")

        # Map
        # Determine selected station from session state
        sel_id = st.session_state.get("report_station_id", None)
        if sel_id == 0: sel_id = None
        
        # Dynamic key forces re-render (and popup show) when selection changes
        map_key = f"map_{sel_id}" if sel_id else "map_default"
        
        m = render_map(stations, highlight_plz=postal_code.strip() if postal_code else None, selected_station_id=sel_id)
        output = st_folium(m, width="100%", height=500, returned_objects=["last_object_clicked"], key=map_key)

    with col2:
        st.subheader("Station Actions")
        
        # Initialize session state vars
        if "report_station_id" not in st.session_state:
            st.session_state["report_station_id"] = 0
        if "last_processed_click" not in st.session_state:
            st.session_state["last_processed_click"] = None
        if "submission_success" not in st.session_state:
            st.session_state["submission_success"] = False
        if "submission_error" not in st.session_state:
            st.session_state["submission_error"] = None

        # Map Click Logic - Only update if changed
        if output and output.get("last_object_clicked"):
            clicked = output["last_object_clicked"]
            if clicked != st.session_state["last_processed_click"]:
                st.session_state["last_processed_click"] = clicked
                if clicked:
                    lat = clicked.get("lat")
                    lng = clicked.get("lng")
                    found = next((s for s in charging_repo.get_all() if abs(s.latitude - lat) < 0.0001 and abs(s.longitude - lng) < 0.0001), None)
                    if found:
                        st.session_state["report_station_id"] = found.station_id

        # Submission Callback
        def submit_report():
            s_id = st.session_state.report_station_id
            content = st.session_state.report_content
            
            if not s_id:
                st.session_state["submission_error"] = "Please enter a valid Station ID."
                return

            try:
                malfunction_service.file_malfunction_report(int(s_id), content)
                st.session_state["submission_success"] = True
                # Clear inputs safely here (Callback runs BEFORE widget rendering of next run)
                st.session_state["report_station_id"] = 0
                st.session_state["report_content"] = ""
            except ValueError as ve:
                st.session_state["submission_error"] = str(ve)
            except Exception as e:
                 st.session_state["submission_error"] = f"An unexpected error occurred: {e}"

        with st.expander("Report a Malfunction", expanded=True):
            st.write("See a broken charger? Let us know.")
            
            station_id_input = st.number_input("Station ID", min_value=0, step=1, help="Found on the station housing or map pin", key="report_station_id")
            
            if "report_content" not in st.session_state:
                st.session_state["report_content"] = ""
            report_text = st.text_area("Describe the issue", max_chars=200, key="report_content")
            
            # Button with Callback
            st.button("Submit Report", type="primary", on_click=submit_report)

            # Render Messages (Post-rerun)
            if st.session_state["submission_success"]:
                st.balloons()
                st.success("Report submitted successfully!")
                st.session_state["submission_success"] = False # Reset for next interactions
            
            if st.session_state["submission_error"]:
                st.error(st.session_state["submission_error"])
                st.session_state["submission_error"] = None

# ------------------------------------------------------------
# ADMIN VIEW
# ------------------------------------------------------------
def render_admin_view():
    st.title("🛡️ Admin Dashboard")
    st.markdown("Overview of network health and reported malfunctions.")
    
    # 1. KPI Metrics
    affected_ids = malfunction_service.report_repository.get_affected_station_ids()
    total_stations = len(charging_repo.get_all())
    affected_count = len(affected_ids)
    
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Total Stations", total_stations)
    kpi2.metric("Affected Stations", affected_count, delta=affected_count if affected_count > 0 else None, delta_color="inverse")
    
    # Calculate Total Reports
    total_reports = sum(malfunction_service.report_repository.count_reports(sid) for sid in affected_ids)
    kpi3.metric("Total Active Reports", total_reports)
    
    st.divider()
    
    # 2. Interactive Dataframe
    st.subheader("Active Issues")
    st.caption("👈 **Select a row** in the table below to view details and resolve issues.")
    
    if not affected_ids:
        st.success("No active malfunctions reported! System is 100% operational.")
        return

    # Build Dataframe for display
    data = []
    for sid in affected_ids:
        count = malfunction_service.report_repository.count_reports(sid)
        is_disabled = not charging_repo._stations[sid].available if sid < len(charging_repo._stations) else False # Simple check, assumes ID=index mostly or repo access
        # Better: check availability via repo
        try:
             # Find station object (inefficient list search but okay for prototype)
             # In production, repo should have get_by_id
             station = next((s for s in charging_repo.get_all() if s.station_id == sid), None)
             status = "🔴 Unavailable" if station and not station.available else "🟡 Warning"
        except:
            status = "Unknown"
            
        data.append({
            "Station ID": sid,
            "Reports": count,
            "Status": status
        })
    
    df = pd.DataFrame(data)
    
    # Modern Streamlit Selection
    event = st.dataframe(
        df,
        selection_mode="single-row",
        on_select="rerun",
        hide_index=True,
        use_container_width=True,
    )
    
    # 3. Detail View & Action
    rows = event.selection.rows
    if rows:
        selected_index = rows[0]
        selected_row = df.iloc[selected_index]
        sel_id = int(selected_row["Station ID"])
        
        st.divider()
        col_det1, col_det2 = st.columns([2, 1])
        
        with col_det1:
            st.markdown(f"### Details for Station `{sel_id}`")
            st.info(f"Current Status: **{selected_row['Status']}** | Reports: **{selected_row['Reports']}**")
            
            # Show actual report texts
            all_reports = malfunction_service.report_repository.all_reports()
            station_reports = [r for r in all_reports if r.station_id == sel_id]
            
            for i, r in enumerate(station_reports, 1):
                st.text(f"{i}. {r.report_text}")

        with col_det2:
            st.markdown("### Actions")
            
            # Check threshold
            current_reports = int(selected_row['Reports'])
            can_repair = current_reports >= 5
            
            if st.button("✅ Mark Repair Completed", type="primary", use_container_width=True, disabled=not can_repair):
                try:
                    events = malfunction_service.mark_repair_completed(sel_id)
                    st.success(f"Station {sel_id} restored!")
                    st.cache_data.clear() # Clear cache if needed, though services are resource cached
                    st.json([event_to_dict(e) for e in events])
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
            
            if not can_repair:
                st.caption(f"⚠️ **Cannot repair**: Station needs at least 5 reports (Current: {current_reports}).")
    else:
        st.caption("Select a row in the table above to view details and perform actions.")

# ------------------------------------------------------------
# Main Routine
# ------------------------------------------------------------
def main():
    role = sidebar_role_switcher()
    
    if role == "USER":
        render_user_view()
    else:
        render_admin_view()

if __name__ == "__main__":
    main()
