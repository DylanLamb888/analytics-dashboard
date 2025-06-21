"""Streamlit app for geographic visualization."""

import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime, timedelta

# Configure page
st.set_page_config(
    page_title="Order Analytics - Geographic View",
    page_icon="🗺️",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .stApp {
        background-color: #fafafa;
    }
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a1a1a;
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# API configuration
API_URL = "http://localhost:8000"

@st.cache_data(ttl=60)
def fetch_geographic_data(start_date, end_date):
    """Fetch geographic distribution data from API."""
    try:
        response = requests.get(
            f"{API_URL}/api/metrics/dashboard",
            params={
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
        )
        if response.status_code == 200:
            data = response.json()
            return pd.DataFrame(data['geographic_distribution'])
        else:
            st.error(f"Failed to fetch data: {response.status_code}")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return pd.DataFrame()

def main():
    """Main Streamlit app."""
    st.markdown('<h1 class="main-header">📍 Geographic Sales Distribution</h1>', unsafe_allow_html=True)
    
    # Date range selector
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        days_back = st.selectbox(
            "Select Time Range",
            options=[7, 30, 90, 180],
            index=1,
            format_func=lambda x: f"Last {x} days"
        )
    
    # Calculate dates
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    with col2:
        st.write("Date Range:")
        st.write(f"{start_date.strftime('%b %d, %Y')} - {end_date.strftime('%b %d, %Y')}")
    
    # Fetch data
    df = fetch_geographic_data(start_date, end_date)
    
    if df.empty:
        st.warning("No geographic data available. Please ensure the API is running and data has been uploaded.")
        return
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["📊 Choropleth Map", "📈 State Rankings", "📉 Revenue Distribution"])
    
    with tab1:
        # Choropleth map
        st.subheader("Revenue by State")
        
        # Create the map
        fig = px.choropleth(
            df,
            locations='location',
            locationmode="USA-states",
            color='revenue',
            hover_name='location',
            hover_data={
                'revenue': ':$,.0f',
                'order_count': ':,',
                'percentage_of_total': ':.1f%'
            },
            color_continuous_scale="Blues",
            labels={'revenue': 'Revenue ($)', 'order_count': 'Orders'},
            title="Sales Revenue Distribution by State"
        )
        
        fig.update_layout(
            geo_scope='usa',
            height=600,
            margin={"r":0,"t":50,"l":0,"b":0}
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # State rankings
        st.subheader("Top Performing States")
        
        # Sort by revenue
        df_sorted = df.sort_values('revenue', ascending=False)
        
        # Bar chart
        fig_bar = px.bar(
            df_sorted.head(10),
            x='revenue',
            y='location',
            orientation='h',
            color='revenue',
            color_continuous_scale="Blues",
            labels={'revenue': 'Revenue ($)', 'location': 'State'},
            title="Top 10 States by Revenue"
        )
        
        fig_bar.update_layout(height=400)
        st.plotly_chart(fig_bar, use_container_width=True)
        
        # Metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Top State",
                df_sorted.iloc[0]['location'],
                f"${df_sorted.iloc[0]['revenue']:,.0f}"
            )
        
        with col2:
            st.metric(
                "States with Sales",
                len(df),
                f"Out of 50 states"
            )
        
        with col3:
            avg_revenue = df['revenue'].mean()
            st.metric(
                "Average State Revenue",
                f"${avg_revenue:,.0f}",
                f"{len(df[df['revenue'] > avg_revenue])} above average"
            )
    
    with tab3:
        # Revenue distribution
        st.subheader("Revenue Distribution Analysis")
        
        # Pie chart
        fig_pie = px.pie(
            df.head(10),
            values='revenue',
            names='location',
            title="Revenue Share by Top 10 States"
        )
        
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Summary statistics
        st.subheader("Distribution Statistics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Revenue Statistics**")
            st.write(f"- Total Revenue: ${df['revenue'].sum():,.0f}")
            st.write(f"- Mean Revenue: ${df['revenue'].mean():,.0f}")
            st.write(f"- Median Revenue: ${df['revenue'].median():,.0f}")
            st.write(f"- Std Deviation: ${df['revenue'].std():,.0f}")
        
        with col2:
            st.write("**Order Statistics**")
            st.write(f"- Total Orders: {df['order_count'].sum():,}")
            st.write(f"- Mean Orders/State: {df['order_count'].mean():.0f}")
            st.write(f"- Max Orders (Single State): {df['order_count'].max():,}")
            st.write(f"- Min Orders (Single State): {df['order_count'].min():,}")

if __name__ == "__main__":
    main()