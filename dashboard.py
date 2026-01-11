import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
from datetime import datetime

# 1. Page Config & Custom Styling
st.set_page_config(page_title="CityGuardian | Command Center", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# Header with Last Updated Time
c_head1, c_head2 = st.columns([3, 1])
with c_head1:
    st.title("🛡️ CityGuardian: Executive Command Center")
with c_head2:
    st.caption(f"Last Updated: {datetime.now().strftime('%H:%M:%S')}")
    if st.button("🔄 Refresh Data"):
        st.rerun()

st.markdown("---")

# 2. Data Loading & Global Cleaning
SHEET_ID = '1yHcKcLdv0TEEpEZ3cAWd9A_t8MBE-yk4JuWqJKn0IeI'
# Timestamp forces fresh data from Google (bypasses cache)
SHEET_URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&timestamp={time.time()}'

try:
    df = pd.read_csv(SHEET_URL)
    
    # --- THE CLEANING ENGINE ---
    # 1. Fix Column Names (removes space like "Status ")
    df.columns = [c.strip() for c in df.columns] 
    
    # 2. Fix the "Pending " space issue (The fix you asked for)
    if 'Status' in df.columns:
        df['Status'] = df['Status'].astype(str).str.strip().str.capitalize()
    
    # 3. Clean Categories and Urgency
    if 'Category' in df.columns:
        df['Category'] = df['Category'].astype(str).str.strip()
    if 'Urgency' in df.columns:
        df['Urgency'] = df['Urgency'].astype(str).str.strip().str.lower()

    # 4. Clean Coordinates
    if 'Location' in df.columns:
        coords = df['Location'].str.split(',', expand=True)
        df['lat'] = pd.to_numeric(coords[0], errors='coerce')
        df['lon'] = pd.to_numeric(coords[1], errors='coerce')
        df = df.dropna(subset=['lat', 'lon'])

    # 3. Metrics Calculation
    pending_count = len(df[df['Status'] == 'Pending'])
    resolved_count = len(df[df['Status'] == 'Resolved'])
    total_count = len(df)
    res_rate = (resolved_count / total_count) * 100 if total_count > 0 else 0

    m1, m2, m3, m4 = st.columns(4)

    # Total Inflow
    with m1:
        fig1 = go.Figure(go.Indicator(
            mode = "number", value = total_count,
            title = {"text": "Total Inflow"},
            number = {'font': {'color': "#2c3e50"}}
        ))
        fig1.update_layout(height=150, margin=dict(t=30, b=0))
        st.plotly_chart(fig1, use_container_width=True)

    # Active Cases
    with m2:
        fig2 = go.Figure(go.Indicator(
            mode = "number", value = pending_count,
            title = {"text": "Active Cases ⏳"},
            number = {'font': {'color': "#e74c3c"}} # Red for alert
        ))
        fig2.update_layout(height=150, margin=dict(t=30, b=0))
        st.plotly_chart(fig2, use_container_width=True)

    # Resolved Cases
    with m3:
        fig3 = go.Figure(go.Indicator(
            mode = "number", value = resolved_count,
            title = {"text": "Resolved ✅"},
            number = {'font': {'color': "#27ae60"}} # Green for success
        ))
        fig3.update_layout(height=150, margin=dict(t=30, b=0))
        st.plotly_chart(fig3, use_container_width=True)

    # Success Rate
    with m4:
        fig4 = go.Figure(go.Indicator(
            mode = "number+gauge", value = res_rate,
            number = {'suffix': "%", 'font': {'color': "#2980b9"}},
            title = {"text": "Success Rate"},
            gauge = {'axis': {'range': [None, 100]}, 'bar': {'color': "#2980b9"}}
        ))
        fig4.update_layout(height=150, margin=dict(t=30, b=0))
        st.plotly_chart(fig4, use_container_width=True)

    # 4. Visualizations
    col_left, col_right = st.columns([1, 1.5])

    with col_left:
        st.subheader("📌 Status Overview")
        if total_count > 0:
            fig_status = px.pie(df, names='Status', hole=0.6, 
                                color_discrete_map={'Resolved':'#2ecc71', 'Pending':'#e74c3c'},
                                template="plotly_white")
            fig_status.update_layout(showlegend=True, margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig_status, use_container_width=True)
        else:
            st.info("No data available yet.")

    with col_right:
        st.subheader("🏢 Department Workload")
        if total_count > 0:
            fig_dept = px.histogram(df, y="Category", color="Urgency", 
                                    orientation='h', barmode='group',
                                    color_discrete_map={'high':'#d35400', 'medium':'#f1c40f', 'low':'#3498db'},
                                    template="plotly_white")
            fig_dept.update_layout(margin=dict(t=20, b=20, l=0, r=0))
            st.plotly_chart(fig_dept, use_container_width=True)
        else:
            st.info("Waiting for first report...")

    # 5. Map & Analytics
    st.markdown("---")
    c1, c2 = st.columns([1.5, 1])

    with c1:
        st.subheader("🗺️ Live Issue Map")
        if total_count > 0:
            # Check if we have the 'address' column from your new backend update
            hover_cols = ["Status"]
            if "address" in df.columns:
                hover_cols.append("address") # Shows street name on hover!
                
            fig_map = px.scatter_map(df, lat="lat", lon="lon", color="Urgency", size_max=15, zoom=11,
                                         map_style="carto-positron", title="Issue Distribution",
                                         hover_name="Category", hover_data=hover_cols)
            fig_map.update_layout(margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig_map, use_container_width=True)

    with c2:
        st.subheader("📈 Urgency Trends")
        if total_count > 0:
            fig_sun = px.sunburst(df, path=['Category', 'Urgency'], color='Urgency',
                                  color_discrete_map={'high':'#d35400', 'medium':'#f1c40f', 'low':'#3498db'})
            st.plotly_chart(fig_sun, use_container_width=True)

except Exception as e:
    st.error(f"Waiting for data connection... ({str(e)})")
    
