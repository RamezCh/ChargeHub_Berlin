import streamlit as st
import pandas as pd
from dataclasses import asdict, is_dataclass
from chargehub.config import ChargeHubConfig
from chargehub.malfunction.application.malfunction_service import MalfunctionService
from chargehub.discovery.infrastructure.repositories.charging_station_csv_repository import ChargingStationCSVRepository

def event_to_dict(event: object) -> dict:
    if is_dataclass(event):
        return {"event": event.__class__.__name__, **asdict(event)}
    return {"event": event.__class__.__name__}

class AdminView:
    def __init__(self, 
                 malfunction_service: MalfunctionService,
                 charging_repo: ChargingStationCSVRepository,
                 config: ChargeHubConfig):
        self.malfunction_service = malfunction_service
        self.charging_repo = charging_repo
        self.config = config

    def render(self):
        st.title("🛡️ Admin Dashboard")
        st.markdown("Overview of network health and reported malfunctions.")
        
        # 1. KPI Metrics
        affected_ids = self.malfunction_service.report_repository.get_affected_station_ids()
        total_stations = len(self.charging_repo.get_all())
        affected_count = len(affected_ids)
        
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("Total Stations", total_stations)
        kpi2.metric("Affected Stations", affected_count, delta=affected_count if affected_count > 0 else None, delta_color="inverse")
        
        total_reports = sum(self.malfunction_service.report_repository.count_reports(sid) for sid in affected_ids)
        kpi3.metric("Total Active Reports", total_reports)
        
        st.divider()
        
        # 2. Interactive Dataframe
        st.subheader("Active Issues")
        st.caption("👈 **Select a row** in the table below to view details and resolve issues.")
        
        if not affected_ids:
            st.success("No active malfunctions reported! System is 100% operational.")
            return

        df = self._build_dataframe(affected_ids)
        
        selection = st.dataframe(
            df,
            selection_mode="single-row",
            on_select="rerun",
            hide_index=True,
            use_container_width=True,
        )
        
        # 3. Detail View & Action
        if selection.selection.rows:
            self._render_details(df, selection.selection.rows[0])
        else:
            st.caption("Select a row in the table above to view details and perform actions.")

    def _build_dataframe(self, affected_ids):
        data = []
        for sid in affected_ids:
            count = self.malfunction_service.report_repository.count_reports(sid)
            try:
                 station = next((s for s in self.charging_repo.get_all() if s.station_id == sid), None)
                 status = "🔴 Unavailable" if station and not station.available else "🟡 Warning"
            except:
                status = "Unknown"
                
            data.append({
                "Station ID": sid,
                "Reports": count,
                "Status": status
            })
        return pd.DataFrame(data)

    def _render_details(self, df, row_idx):
        selected_row = df.iloc[row_idx]
        sel_id = int(selected_row["Station ID"])
        
        st.divider()
        col_det1, col_det2 = st.columns([2, 1])
        
        with col_det1:
            st.markdown(f"### Details for Station `{sel_id}`")
            st.info(f"Current Status: **{selected_row['Status']}** | Reports: **{selected_row['Reports']}**")
            
            all_reports = self.malfunction_service.report_repository.all_reports()
            station_reports = [r for r in all_reports if r.station_id == sel_id]
            for i, r in enumerate(station_reports, 1):
                st.text(f"{i}. {r.report_text}")

        with col_det2:
            st.markdown("### Actions")
            current_reports = int(selected_row['Reports'])
            can_repair = current_reports >= self.config.REPAIR_THRESHOLD
            
            if st.button("✅ Mark Repair Completed", type="primary", use_container_width=True, disabled=not can_repair):
                try:
                    events = self.malfunction_service.mark_repair_completed(sel_id)
                    st.success(f"Station {sel_id} restored!")
                    st.cache_data.clear() 
                    st.json([event_to_dict(e) for e in events])
                    if "cached_map" in st.session_state:
                         del st.session_state["cached_map"] # Clear map cache for admin too
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
            
            if not can_repair:
                st.caption(f"⚠️ **Cannot repair**: Station needs at least {self.config.REPAIR_THRESHOLD} reports (Current: {current_reports}).")
