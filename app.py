
import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from dotenv import load_dotenv
from supabase import create_client, Client

# 1. LOAD ENVIRONMENTAL CONFIGS
load_dotenv()

# 2. PAGE INITIALIZATION & PREMIUM THEME DESIGN CSS INJECTION
st.set_page_config(page_title="Apple Style Sales Dashboard", layout="wide")

st.markdown("""
    <style>
        .stApp { background-color: #F3F4F6 !important; }
        .block-container { padding: 0rem 2rem 1rem 2rem !important; }
        .custom-header {
            background-color: #1A1A1A; padding: 20px 30px;
            margin: 0rem -2rem 25px -2rem; color: #FFFFFF;
            display: flex; justify-content: space-between; align-items: center;
            border-bottom: 3px solid #3182ce;
        }
        .custom-header h1 { color: white !important; margin: 0; font-size: 24px; font-weight: 600; }
        .custom-header span { color: #A0AEC0; font-size: 14px; }
        div[data-testid="stMetricValue"] { font-size: 26px !important; font-weight: 700 !important; color: #FFFFFF !important; }
        div[data-testid="stMetricLabel"] { font-size: 13px !important; color: #A0AEC0 !important; font-weight: 500 !important; }
        [data-testid="stMetric"] {
            background-color: #0F172A !important; border: 1px solid #1E293B;
            padding: 15px 20px !important; border-radius: 12px !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="custom-header">
        <h1>Enterprise Sales Performance Analytics</h1>
        <span>Cloud Engine Interface: Connected via Secure Supabase REST API (Port 443)</span>
    </div>
""", unsafe_allow_html=True)

# 3. HIGH-RELIABILITY API FETCH ENGINE (Bypasses Firewall Timeouts)
@st.cache_data
def fetch_cloud_records():
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        st.error("❌ Environment variables missing! Please check your .env file or Streamlit Secrets.")
        st.stop()
        
    # Initialize native API client over HTTPS (Standard port 443)
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Query database records through public gateway
    response = supabase.table('corporate_sales_records').select("*").execute()
    
    data = pd.DataFrame(response.data)
    
    if not data.empty:
        data['order_date'] = pd.to_datetime(data['order_date'])
        data['year'] = data['order_date'].dt.year
    return data

try:
    df = fetch_cloud_records()
    if df.empty:
        st.warning("⚠️ Database connected successfully, but 'corporate_sales_records' table is empty.")
        st.stop()
except Exception as api_err:
    st.error(f"Failed to fetch real-time cloud data layers: {api_err}")
    st.stop()

# 4. TOP FINANCIAL KPI SUMMARY BLOCKS
m1, m2, m3, m4, m5 = st.columns(5)
total_orders = df['order_id'].nunique()
avg_margin = df['profit_margin'].mean()
total_units = df['quantity'].sum()
avg_sales = df['sales'].mean()
total_revenue = df['sales'].sum()

m1.metric("Total Orders Tracked", f"{total_orders:,}")
m2.metric("Avg Profit Margin", f"{avg_margin:.2f}%")
m3.metric("Total Units Sold", f"{total_units:,}")
m4.metric("Avg Order Value", f"${avg_sales:.2f}")
m5.metric("Gross Revenue Return", f"${total_revenue/1000000:.2f}M")

st.markdown("<br>", unsafe_allow_html=True)

# 5. MIDDLE VISUAL LAYOUT (3 GRID PANELS)
mid_col1, mid_col2, mid_col3 = st.columns([1, 1.5, 1])

with mid_col1:
    st.markdown('<div style="background-color: white; padding: 15px; border-radius: 10px;">', unsafe_allow_html=True)
    st.caption("**Sales Split by Customer Segment**")
    segment_df = df.groupby('segment')['sales'].sum().reset_index()
    fig_donut = px.pie(segment_df, names='segment', values='sales', hole=0.6, color_discrete_sequence=px.colors.qualitative.Pastel)
    fig_donut.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=255)
    st.plotly_chart(fig_donut, width='stretch')
    st.markdown('</div>', unsafe_allow_html=True)

with mid_col2:
    st.markdown('<div style="background-color: white; padding: 15px; border-radius: 10px;">', unsafe_allow_html=True)
    st.caption("**Historical Revenue Inflow Trend & Categories Stack**")
    trend_df = df.groupby(['year', 'category'])['sales'].sum().reset_index()
    fig_trend = px.bar(trend_df, x='year', y='sales', color='category', barmode='stack', color_discrete_sequence=['#3182ce', '#63b3ed', '#90cdf4'])
    fig_trend.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=255, template="plotly_white")
    st.plotly_chart(fig_trend, width='stretch')
    st.markdown('</div>', unsafe_allow_html=True)

with mid_col3:
    st.markdown('<div style="background-color: white; padding: 15px; border-radius: 10px;">', unsafe_allow_html=True)
    st.caption("**Top Performing States Growth Engine**")
    state_df = df.groupby('state')['sales'].sum().reset_index().sort_values('sales', ascending=False).head(5)
    fig_state = px.bar(state_df, y='state', x='sales', orientation='h', color_discrete_sequence=['#3182ce'])
    fig_state.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=255, template="plotly_white")
    st.plotly_chart(fig_state, width='stretch')
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 6. BOTTOM RISK MATRIX LAYER (4 DEEP-DIVE PANELS)
bot_col1, bot_col2, bot_col3, bot_col4 = st.columns(4)

with bot_col1:
    st.markdown('<div style="background-color: white; padding: 15px; border-radius: 10px;">', unsafe_allow_html=True)
    st.caption("**Volume Clusters vs Value Return**")
    qty_df = df.groupby('quantity')['sales'].sum().reset_index()
    fig_qty = px.bar(qty_df, x='quantity', y='sales', color_discrete_sequence=['#3182ce'])
    fig_qty.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=200, template="plotly_white")
    st.plotly_chart(fig_qty, width='stretch')
    st.markdown('</div>', unsafe_allow_html=True)

with bot_col2:
    st.markdown('<div style="background-color: white; padding: 15px; border-radius: 10px;">', unsafe_allow_html=True)
    st.caption("**Order Densities across Discount Tiers**")
    disc_df = df.groupby('discount')['order_id'].count().reset_index()
    disc_df['discount'] = disc_df['discount'].astype(str)
    fig_disc = px.bar(disc_df, x='discount', y='order_id', color_discrete_sequence=['#4299e1'])
    fig_disc.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=200, template="plotly_white")
    st.plotly_chart(fig_disc, width='stretch')
    st.markdown('</div>', unsafe_allow_html=True)

with bot_col3:
    st.markdown('<div style="background-color: white; padding: 15px; border-radius: 10px;">', unsafe_allow_html=True)
    st.caption("**Revenue Return by Product Sub-Category**")
    sub_df = df.groupby('sub_category')['sales'].sum().reset_index().sort_values('sales', ascending=False).head(6)
    fig_sub = px.bar(sub_df, y='sub_category', x='sales', orientation='h', color_discrete_sequence=['#63b3ed'])
    fig_sub.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=200, template="plotly_white")
    st.plotly_chart(fig_sub, width='stretch')
    st.markdown('</div>', unsafe_allow_html=True)

with bot_col4:
    st.markdown('<div style="background-color: white; padding: 15px; border-radius: 10px;">', unsafe_allow_html=True)
    st.caption("**Regional Contribution and Segment Leakage**")
    reg_df = df.groupby(['region', 'segment'])['sales'].sum().reset_index()
    fig_reg = px.bar(reg_df, x='region', y='sales', color='segment', barmode='stack', color_discrete_sequence=['#2b6cb0', '#4299e1', '#bee3f8'])
    fig_reg.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=200, template="plotly_white")
    st.plotly_chart(fig_reg, width='stretch')
    st.markdown('</div>', unsafe_allow_html=True)