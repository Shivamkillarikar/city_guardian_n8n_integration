import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time

# 1. Page Config & Custom Styling
st.set_page_config(page_title="CityGuardian | Command Center", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ CityGuardian: Executive Command Center")
st.markdown("---")

# 2. Data Loading & Global Cleaning
SHEET_ID = '1yHcKcLdv0TEEpEZ3cAWd9A_t8MBE-yk4JuWqJKn0IeI'
# Added a timestamp to the URL to force Google to bypass its 5-minute cache
SHEET_URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&timestamp={time.time()}'

try:
    df = pd.read_csv(SHEET_URL)
    
    # --- GLOBAL CLEANING (Fixes everything at once) ---
    df.columns = [c.strip() for c in df.columns] # Strip spaces from headers
    
    if 'Status' in df.columns:
        df['Status'] = df['Status'].astype(str).str.strip().str.capitalize()
    
    if 'Category' in df.columns:
        df['Category'] = df['Category'].astype(str).str.strip()
        
    if 'Urgency' in df.columns:
        df['Urgency'] = df['Urgency'].astype(str).str.strip().str.lower()

    # Clean Coordinates
    if 'Location' in df.columns:
        coords = df['Location'].str.split(',', expand=True)
        df['lat'] = pd.to_numeric(coords[0], errors='coerce')
        df['lon'] = pd.to_numeric(coords[1], errors='coerce')
        df = df.dropna(subset=['lat', 'lon'])

    # 3. Top Row Metrics
    # Now that data is cleaned globally, these filters will work perfectly
    pending_count = len(df[df['Status'] == 'Pending'])
    resolved_count = len(df[df['Status'] == 'Resolved'])
    res_rate = (resolved_count / len(df)) * 100 if len(df) > 0 else 0

    m1, m2, m3, m4 = st.columns(4)

    # Total Inflow Card
    with m1:
        fig1 = go.Figure(go.Indicator(
            mode = "number",
            value = len(df),
            title = {"text": "Total Inflow"},
            number = {'font': {'color': "#2c3e50"}}
        ))
        fig1.update_layout(height=150, margin=dict(t=30, b=0))
        st.plotly_chart(fig1, use_container_width=True)

    # Active Cases Card
    with m2:
        if pending_count == 0:
            st.warning(f"No Pending cases found. Check status column!")
            
        fig2 = go.Figure(go.Indicator(
            mode = "number",
            value = pending_count,
            title = {"text": "Active Cases ⏳"},
            number = {'font': {'color': "#e74c3c"}}
        ))
        fig2.update_layout(height=150, margin=dict(t=30, b=0))
        st.plotly_chart(fig2, use_container_width=True)

    # Resolved Card
    with m3:
        fig3 = go.Figure(go.Indicator(
            mode = "number",
            value = resolved_count,
            title = {"text": "Resolved ✅"},
            number = {'font': {'color': "#27ae60"}}
        ))
        fig3.update_layout(height=150, margin=dict(t=30, b=0))
        st.plotly_chart(fig3, use_container_width=True)

    # Resolution Rate Card
    with m4:
        fig4 = go.Figure(go.Indicator(
            mode = "number+gauge",
            value = res_rate,
            number = {'suffix': "%", 'font': {'color': "#2980b9"}},
            title = {"text": "Success Rate"},
        ))
        fig4.update_layout(height=150, margin=dict(t=30, b=0))
        st.plotly_chart(fig4, use_container_width=True)

    # 4. Advanced Visualizations
    col_left, col_right = st.columns([1, 1.5])

    with col_left:
        st.subheader("📌 Status Overview")
        fig_status = px.pie(df, names='Status', hole=0.6, 
                            color_discrete_map={'Resolved':'#2ecc71', 'Pending':'#e74c3c'},
                            template="plotly_white")
        fig_status.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_status, use_container_width=True)

    with col_right:
        st.subheader("🏢 Department Workload")
        fig_dept = px.histogram(df, y="Category", color="Urgency", 
                                orientation='h', barmode='group',
                                color_discrete_map={'high':'#d35400', 'medium':'#f1c40f', 'low':'#3498db'},
                                template="plotly_white")
        fig_dept.update_layout(margin=dict(t=20, b=20, l=0, r=0))
        st.plotly_chart(fig_dept, use_container_width=True)

    # 5. Map & Analytics
    st.markdown("---")
    c1, c2 = st.columns([1.5, 1])

    with c1:
        st.subheader("🗺️ Live Issue Map")
        fig_map = px.scatter_map(df, lat="lat", lon="lon", color="Urgency", size_max=15, zoom=10,
                                     map_style="carto-positron", title="Issue Distribution",
                                     hover_name="Category", hover_data=["Status"])
        fig_map.update_layout(margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_map, use_container_width=True)

    with c2:
        st.subheader("📈 Urgency Trends")
        fig_sun = px.sunburst(df, path=['Category', 'Urgency'], color='Urgency',
                              color_discrete_map={'high':'#d35400', 'medium':'#f1c40f', 'low':'#3498db'})
        st.plotly_chart(fig_sun, use_container_width=True)

except Exception as e:
    st.error(f"Error: {e}")
    
