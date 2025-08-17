import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import warnings
import logging
import gc
warnings.filterwarnings('ignore')

from modules.data_processor import DataProcessor
from modules.customer_analytics import CustomerAnalytics
from modules.sales_analytics import SalesAnalytics
from modules.geographic_analytics import GeographicAnalytics
from brand_config import get_brand_css, get_available_themes, get_available_fonts
from config import Config
from utils import performance_monitor, safe_execute, SecurityUtils, PerformanceMonitor
from auth import require_authentication, init_auth_session

# Configure logging
logging.basicConfig(**Config.get_logging_config())
logger = logging.getLogger(__name__)

# Validate configuration with caching
@st.cache_data
def validate_app_config():
    return Config.validate_config()

if not validate_app_config():
    st.error("❌ Configuration validation failed. Please check logs.")
    st.stop()

st.set_page_config(
    page_title=Config.APP_NAME,
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize authentication with session state
if 'auth_initialized' not in st.session_state:
    init_auth_session()
    st.session_state.auth_initialized = True

require_authentication()

@st.cache_data
def load_custom_css():
    st.markdown("""
    <style>
    /* Executive Professional Color Scheme */
    :root {
        --primary-navy: #1B365D;
        --secondary-blue: #2E5984;
        --accent-gold: #C5912B;
        --light-gray: #F8F9FA;
        --medium-gray: #E9ECEF;
        --text-dark: #2C3E50;
        --success-green: #27AE60;
        --warning-orange: #F39C12;
        --danger-red: #E74C3C;
        --executive-gradient: linear-gradient(135deg, #1B365D 0%, #2E5984 50%, #3498DB 100%);
    }
    
    /* Main Layout */
    .main {
        padding: 0rem 1rem;
        background-color: var(--light-gray);
    }
    
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        max-width: none;
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    /* Executive Dashboard Header */
    .executive-header {
        background: var(--executive-gradient);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 25px rgba(27, 54, 93, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .executive-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 100%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
        transform: rotate(45deg);
        animation: shine 3s infinite;
    }
    
    @keyframes shine {
        0% { transform: translateX(-100%) rotate(45deg); }
        100% { transform: translateX(200%) rotate(45deg); }
    }
    
    .executive-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .executive-subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
        font-weight: 300;
        margin: 0;
    }
    
    /* Premium Metric Cards */
    .executive-metric {
        background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid var(--primary-navy);
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .executive-metric:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .executive-metric h3 {
        font-size: 2.2rem;
        font-weight: 700;
        color: var(--primary-navy);
        margin-bottom: 0.5rem;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .executive-metric p {
        color: var(--text-dark);
        font-size: 1rem;
        font-weight: 500;
        margin: 0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .executive-metric small {
        color: #6c757d;
        font-size: 0.85rem;
        display: block;
        margin-top: 0.5rem;
    }
    
    /* Segment-specific styling */
    .segment-champions { border-left-color: var(--success-green); }
    .segment-loyal { border-left-color: var(--secondary-blue); }
    .segment-potential { border-left-color: var(--accent-gold); }
    .segment-risk { border-left-color: var(--warning-orange); }
    .segment-lost { border-left-color: var(--danger-red); }
    
    /* Professional Section Headers */
    .section-header {
        background: linear-gradient(90deg, var(--primary-navy) 0%, var(--secondary-blue) 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        margin: 1.5rem 0 1rem 0;
        font-size: 1.3rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        box-shadow: 0 4px 10px rgba(27, 54, 93, 0.2);
    }
    
    /* Enhanced Sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, var(--primary-navy) 0%, var(--secondary-blue) 100%);
    }
    
    .css-1d391kg .css-10trblm {
        color: white;
    }
    
    /* Form Controls */
    .stSelectbox > div > div > div > div {
        background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
        border: 2px solid var(--medium-gray);
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    .stSelectbox > div > div > div > div:focus {
        border-color: var(--primary-navy);
        box-shadow: 0 0 10px rgba(27, 54, 93, 0.2);
    }
    
    /* Enhanced Typography */
    h1, h2, h3 {
        color: var(--primary-navy);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: 600;
    }
    
    h1 {
        border-bottom: 3px solid var(--accent-gold);
        padding-bottom: 10px;
        margin-bottom: 20px;
    }
    
    /* Data Tables */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Chart Containers */
    .js-plotly-plot {
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        background: white;
    }
    
    /* Executive Summary Cards */
    .summary-card {
        background: linear-gradient(135deg, var(--primary-navy) 0%, var(--secondary-blue) 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(27, 54, 93, 0.3);
    }
    
    .summary-card h4 {
        color: white;
        margin-bottom: 1rem;
        font-size: 1.3rem;
        font-weight: 600;
    }
    
    .summary-card .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--accent-gold);
        margin-bottom: 0.5rem;
    }
    
    /* Status Indicators */
    .status-excellent { 
        background: linear-gradient(135deg, var(--success-green) 0%, #2ECC71 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        text-align: center;
    }
    
    .status-good { 
        background: linear-gradient(135deg, var(--secondary-blue) 0%, #3498DB 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        text-align: center;
    }
    
    .status-warning { 
        background: linear-gradient(135deg, var(--warning-orange) 0%, #F7B942 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        text-align: center;
    }
    
    .status-critical { 
        background: linear-gradient(135deg, var(--danger-red) 0%, #EC7063 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        text-align: center;
    }
    
    /* Loading Animation */
    .loading-spinner {
        border: 4px solid var(--medium-gray);
        border-top: 4px solid var(--primary-navy);
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
        margin: 20px auto;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .executive-title {
            font-size: 2rem;
        }
        
        .executive-metric h3 {
            font-size: 1.8rem;
        }
        
        .executive-header {
            padding: 1.5rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

@performance_monitor("main_application")
def main():
    # Load custom CSS styling
    load_custom_css()
    
    # Log application start
    logger.info("Customer Analytics Dashboard started")
    
    # Display memory usage in development
    if Config.DEBUG:
        memory_usage = PerformanceMonitor.get_memory_usage()
        st.sidebar.caption(f"Memory: {memory_usage['rss_mb']:.1f}MB")
    
    # Initialize variables to avoid undefined reference errors
    company_name = ""
    logo_url = ""
    
    # Sidebar for upload, format controls, and brand customization
    with st.sidebar:
        # Brand Customization Section
        st.header("🎨 Brand Settings")
        
        # Theme selection
        available_themes = get_available_themes()
        theme_options = {theme[1]: theme[0] for theme in available_themes}
        selected_theme_name = st.selectbox(
            "Select Brand Theme",
            options=list(theme_options.keys()),
            help="Choose a color theme that matches your brand"
        )
        selected_theme = theme_options[selected_theme_name]
        
        # Font selection
        available_fonts = get_available_fonts()
        font_options = {font[1]: font[0] for font in available_fonts}
        selected_font_name = st.selectbox(
            "Select Font Family",
            options=list(font_options.keys()),
            help="Choose a font family for the dashboard"
        )
        selected_font = font_options[selected_font_name]
        
        # Company name (optional)
        company_name = st.text_input(
            "Company Name (Optional)",
            placeholder="Your Company Name",
            help="Display your company name in the header"
        )
        
        # Logo URL (optional)
        logo_url = st.text_input(
            "Logo URL (Optional)",
            placeholder="https://example.com/logo.png",
            help="URL to your company logo"
        )
        
        # Apply brand customization
        brand_css = get_brand_css(
            theme_key=selected_theme,
            font_family=selected_font,
            company_name=company_name,
            logo_url=logo_url
        )
        st.markdown(brand_css, unsafe_allow_html=True)
        
        st.divider()
        
        st.header("📂 Data Upload")
        uploaded_file = st.file_uploader(
            "Upload Customer Transaction Data",
            type=['csv'],
            help="Upload CSV file with customer transaction data"
        )
        
        # Initialize variables
        analysis_type = None
        date_range = None
        df = None
        
        if uploaded_file is not None:
            # Validate file security
            is_valid, message = SecurityUtils.validate_file_upload(uploaded_file)
            if not is_valid:
                st.error(f"❌ File validation failed: {message}")
                return
            
            def load_data():
                processor = DataProcessor()
                return processor.load_and_validate_data(uploaded_file)
            
            df = safe_execute(load_data, "data loading")
            
            if df is not None:
                # Check memory usage after loading
                if not PerformanceMonitor.check_memory_threshold():
                    st.warning("⚠️ High memory usage detected. Consider using a smaller dataset.")
                
                # Limit records if necessary
                if len(df) > Config.MAX_RECORDS:
                    st.warning(f"⚠️ Dataset has {len(df):,} records. Limiting to {Config.MAX_RECORDS:,} for performance.")
                    df = df.head(Config.MAX_RECORDS)
                
                st.success(f"✅ Data loaded: {len(df):,} records")
                logger.info(f"Data loaded successfully: {len(df)} records")
                
                st.header("🔧 Analysis Options")
                analysis_type = st.selectbox(
                    "Select Analysis",
                    ["Executive Summary", "Overview", "Customer Segmentation", "Sales Performance", "Geographic Analysis", "Advanced Analytics"]
                )
                
                date_range = st.date_input(
                    "Date Range",
                    value=(df['order_date'].min().date(), df['order_date'].max().date()),
                    min_value=df['order_date'].min().date(),
                    max_value=df['order_date'].max().date()
                )
                        
            else:
                st.error("❌ Failed to load data. Please check file format.")
                logger.error("Data loading failed")
    
    # Executive Dashboard Header with Branding
    company_display = f'<div class="company-brand company-name">{company_name}</div>' if company_name else ''
    logo_display = f'<img src="{logo_url}" alt="Company Logo" class="company-logo" style="max-height: 60px; margin-bottom: 10px;" />' if logo_url else ''
    
    st.markdown(f'''
    <div class="executive-header">
        {company_display}
        {logo_display}
        <h1 class="executive-title">📊 Executive Analytics Dashboard</h1>
        <p class="executive-subtitle">Strategic Customer Intelligence & Business Performance Platform</p>
    </div>
    ''', unsafe_allow_html=True)
    
    if uploaded_file is not None and df is not None and date_range is not None and len(date_range) == 2:
        start_date, end_date = date_range
        mask = (df['order_date'].dt.date >= start_date) & (df['order_date'].dt.date <= end_date)
        filtered_df = df[mask].copy()
        
        @st.cache_resource
        def create_analytics(_df):
            customer_analytics = CustomerAnalytics(_df)
            sales_analytics = SalesAnalytics(_df)
            geographic_analytics = GeographicAnalytics(_df)
            return customer_analytics, sales_analytics, geographic_analytics
        
        analytics_result = safe_execute(lambda: create_analytics(filtered_df), "analytics initialization")
        
        if analytics_result:
            customer_analytics, sales_analytics, geographic_analytics = analytics_result
            
            # Execute analysis based on type
            try:
                if analysis_type == "Executive Summary":
                    show_executive_summary(filtered_df, customer_analytics, sales_analytics, geographic_analytics)
                elif analysis_type == "Overview":
                    show_overview(filtered_df, customer_analytics, sales_analytics)
                elif analysis_type == "Customer Segmentation":
                    show_customer_segmentation(customer_analytics)
                elif analysis_type == "Sales Performance":
                    show_sales_performance(sales_analytics)
                elif analysis_type == "Geographic Analysis":
                    show_geographic_analysis(geographic_analytics)
                elif analysis_type == "Advanced Analytics":
                    show_advanced_analytics(customer_analytics, sales_analytics)
                
                # Force garbage collection after analysis
                del customer_analytics, sales_analytics, geographic_analytics
                gc.collect()
                
            except Exception as e:
                logger.error(f"Error in {analysis_type} analysis: {str(e)}")
                st.error(f"❌ Error in {analysis_type}: {str(e)}")
        else:
            st.error("❌ Failed to initialize analytics modules")
    else:
        show_sample_data_info()

def show_executive_summary(df, customer_analytics, sales_analytics, geographic_analytics):
    st.markdown('<div class="section-header">📈 Executive Summary</div>', unsafe_allow_html=True)
    
    # Key Performance Indicators
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_revenue = df['total_amount'].sum()
    total_customers = df['customer_id'].nunique()
    avg_order_value = df['total_amount'].mean()
    total_orders = len(df)
    
    # Calculate growth metrics
    df_sorted = df.sort_values('order_date')
    mid_point = len(df_sorted) // 2
    first_half_revenue = df_sorted.iloc[:mid_point]['total_amount'].sum()
    second_half_revenue = df_sorted.iloc[mid_point:]['total_amount'].sum()
    growth_rate = ((second_half_revenue - first_half_revenue) / first_half_revenue * 100) if first_half_revenue > 0 else 0
    
    with col1:
        st.markdown(f'''
        <div class="executive-metric">
            <h3>${total_revenue:,.0f}</h3>
            <p>Total Revenue</p>
            <small>Period Performance</small>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'''
        <div class="executive-metric">
            <h3>{total_customers:,}</h3>
            <p>Active Customers</p>
            <small>Unique Buyers</small>
        </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'''
        <div class="executive-metric">
            <h3>${avg_order_value:.0f}</h3>
            <p>Avg Order Value</p>
            <small>Per Transaction</small>
        </div>
        ''', unsafe_allow_html=True)
    
    with col4:
        st.markdown(f'''
        <div class="executive-metric">
            <h3>{total_orders:,}</h3>
            <p>Total Orders</p>
            <small>Transactions</small>
        </div>
        ''', unsafe_allow_html=True)
    
    with col5:
        growth_status = "status-excellent" if growth_rate > 10 else "status-good" if growth_rate > 0 else "status-warning" if growth_rate > -10 else "status-critical"
        st.markdown(f'''
        <div class="executive-metric">
            <h3>{growth_rate:.1f}%</h3>
            <p>Growth Rate</p>
            <small class="{growth_status}">Period Comparison</small>
        </div>
        ''', unsafe_allow_html=True)
    
    # Strategic Insights Section
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="section-header">🎯 Customer Intelligence</div>', unsafe_allow_html=True)
        
        # Customer segments for executive view
        segments = customer_analytics.get_customer_segments()
        
        # Executive customer summary
        champions_count = segments.get('Champions', {}).get('count', 0)
        total_segment_customers = sum([seg.get('count', 0) for seg in segments.values()])
        champion_percentage = (champions_count / total_segment_customers * 100) if total_segment_customers > 0 else 0
        
        st.markdown(f'''
        <div class="summary-card">
            <h4>Customer Portfolio Health</h4>
            <div class="metric-value">{champion_percentage:.1f}%</div>
            <p>High-Value Champions</p>
            <small>{champions_count:,} of {total_segment_customers:,} customers</small>
        </div>
        ''', unsafe_allow_html=True)
        
        # CLV insights
        try:
            clv_data = customer_analytics.calculate_customer_lifetime_value()
            if not clv_data.empty:
                avg_clv = clv_data['clv'].mean()
                high_value_customers = len(clv_data[clv_data['clv'] > avg_clv * 1.5])
                
                st.markdown(f'''
                <div class="summary-card">
                    <h4>Customer Lifetime Value</h4>
                    <div class="metric-value">${avg_clv:.0f}</div>
                    <p>Average CLV</p>
                    <small>{high_value_customers:,} high-value customers identified</small>
                </div>
                ''', unsafe_allow_html=True)
        except:
            pass
    
    with col2:
        st.markdown('<div class="section-header">📊 Business Performance</div>', unsafe_allow_html=True)
        
        # Sales performance metrics
        metrics = sales_analytics.get_sales_metrics()
        repeat_rate = metrics.get('repeat_customer_rate', 0)
        
        repeat_status = "status-excellent" if repeat_rate > 40 else "status-good" if repeat_rate > 25 else "status-warning"
        
        st.markdown(f'''
        <div class="summary-card">
            <h4>Customer Retention</h4>
            <div class="metric-value">{repeat_rate:.1f}%</div>
            <p>Repeat Purchase Rate</p>
            <small class="{repeat_status}">Customer Loyalty Indicator</small>
        </div>
        ''', unsafe_allow_html=True)
        
        # Revenue concentration
        top_20_percent = int(total_customers * 0.2)
        customer_revenue = df.groupby('customer_id')['total_amount'].sum().sort_values(ascending=False)
        top_20_revenue = customer_revenue.head(top_20_percent).sum()
        revenue_concentration = (top_20_revenue / total_revenue * 100) if total_revenue > 0 else 0
        
        concentration_status = "status-warning" if revenue_concentration > 80 else "status-good"
        
        st.markdown(f'''
        <div class="summary-card">
            <h4>Revenue Concentration</h4>
            <div class="metric-value">{revenue_concentration:.1f}%</div>
            <p>Top 20% Customers</p>
            <small class="{concentration_status}">Risk Distribution</small>
        </div>
        ''', unsafe_allow_html=True)
    
    # Strategic Recommendations
    st.markdown('<div class="section-header">💡 Strategic Recommendations</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('''
        <div class="summary-card">
            <h4>🎯 Customer Focus</h4>
            <ul style="list-style: none; padding-left: 0;">
                <li>• Expand Champion customer base</li>
                <li>• Implement retention campaigns for At-Risk segments</li>
                <li>• Develop loyalty programs for repeat customers</li>
            </ul>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown('''
        <div class="summary-card">
            <h4>📈 Revenue Growth</h4>
            <ul style="list-style: none; padding-left: 0;">
                <li>• Increase average order value through upselling</li>
                <li>• Focus on high-margin product categories</li>
                <li>• Optimize pricing strategies</li>
            </ul>
        </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        st.markdown('''
        <div class="summary-card">
            <h4>🚀 Market Expansion</h4>
            <ul style="list-style: none; padding-left: 0;">
                <li>• Target underperforming geographic regions</li>
                <li>• Develop new customer acquisition channels</li>
                <li>• Analyze competitive positioning</li>
            </ul>
        </div>
        ''', unsafe_allow_html=True)

def show_overview(df, customer_analytics, sales_analytics):
    st.header("📊 Business Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_revenue = df['total_amount'].sum()
        st.markdown(f'<div class="executive-metric"><h3>${total_revenue:,.0f}</h3><p>Total Revenue</p></div>', unsafe_allow_html=True)
    
    with col2:
        total_customers = df['customer_id'].nunique()
        st.markdown(f'<div class="executive-metric"><h3>{total_customers:,}</h3><p>Total Customers</p></div>', unsafe_allow_html=True)
    
    with col3:
        total_orders = len(df)
        st.markdown(f'<div class="executive-metric"><h3>{total_orders:,}</h3><p>Total Orders</p></div>', unsafe_allow_html=True)
    
    with col4:
        avg_order_value = df['total_amount'].mean()
        st.markdown(f'<div class="executive-metric"><h3>${avg_order_value:.2f}</h3><p>Avg Order Value</p></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Revenue Trend")
        daily_revenue = df.groupby(df['order_date'].dt.date)['total_amount'].sum().reset_index()
        fig = px.line(daily_revenue, x='order_date', y='total_amount', 
                     title="Daily Revenue Trend")
        fig.update_traces(line_color='#1f77b4', line_width=3)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🏆 Top Products")
        top_products = df.groupby('product_name')['total_amount'].sum().sort_values(ascending=False).head(10)
        fig = px.bar(x=top_products.values, y=top_products.index, orientation='h',
                    title="Top 10 Products by Revenue")
        fig.update_traces(marker_color='#17a2b8')
        st.plotly_chart(fig, use_container_width=True)

def show_customer_segmentation(customer_analytics):
    st.header("👥 Customer Segmentation")
    
    segments = customer_analytics.get_customer_segments()
    
    col1, col2, col3 = st.columns(3)
    
    segment_colors = {'Champions': '#28a745', 'Loyal Customers': '#17a2b8', 
                     'Potential Loyalists': '#ffc107', 'At Risk': '#fd7e14', 
                     'Lost Customers': '#dc3545'}
    
    for i, (segment, data) in enumerate(segments.items()):
        col = [col1, col2, col3][i % 3]
        with col:
            segment_class = 'segment-champions' if segment == 'Champions' else 'segment-loyal' if segment == 'Loyal Customers' else 'segment-potential' if segment == 'Potential Loyalists' else 'segment-risk' if segment == 'At Risk' else 'segment-lost'
            st.markdown(f'''
            <div class="executive-metric {segment_class}">
                <h3>{data["count"]:,}</h3>
                <p>{segment}</p>
                <small>${data["revenue"]:,.0f} revenue</small>
            </div>
            ''', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 RFM Analysis")
        rfm_data = customer_analytics.calculate_rfm()
        
        fig = px.scatter_3d(rfm_data, x='recency', y='frequency', z='monetary',
                           color='segment', title="3D RFM Segmentation",
                           color_discrete_map=segment_colors)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("💰 Customer Lifetime Value")
        clv_data = customer_analytics.calculate_customer_lifetime_value()
        
        fig = px.histogram(clv_data, x='clv', nbins=30, 
                          title="Customer Lifetime Value Distribution")
        fig.update_traces(marker_color='#1f77b4')
        st.plotly_chart(fig, use_container_width=True)

def show_sales_performance(sales_analytics):
    st.header("📈 Sales Performance")
    
    metrics = sales_analytics.get_sales_metrics()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f'<div class="executive-metric"><h3>{metrics["growth_rate"]:.1f}%</h3><p>Revenue Growth</p></div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'<div class="executive-metric"><h3>{metrics["repeat_customer_rate"]:.1f}%</h3><p>Repeat Customer Rate</p></div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'<div class="executive-metric"><h3>{metrics["avg_order_frequency"]:.1f}</h3><p>Avg Order Frequency</p></div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown(f'<div class="executive-metric"><h3>${metrics["revenue_per_customer"]:.2f}</h3><p>Revenue per Customer</p></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Monthly Performance")
        monthly_data = sales_analytics.get_monthly_trends()
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Bar(x=monthly_data.index, y=monthly_data['revenue'], 
                            name="Revenue", marker_color='#1f77b4'))
        fig.add_trace(go.Scatter(x=monthly_data.index, y=monthly_data['customers'], 
                                mode='lines+markers', name="Customers", 
                                line=dict(color='#dc3545', width=3)), secondary_y=True)
        
        fig.update_xaxes(title_text="Month")
        fig.update_yaxes(title_text="Revenue ($)", secondary_y=False)
        fig.update_yaxes(title_text="Customers", secondary_y=True)
        fig.update_layout(title="Monthly Revenue & Customer Trends")
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🛒 Product Performance")
        product_data = sales_analytics.get_product_performance()
        
        fig = px.treemap(product_data, path=['product_name'], values='revenue',
                        title="Product Revenue Treemap")
        st.plotly_chart(fig, use_container_width=True)

def show_geographic_analysis(geographic_analytics):
    st.header("🌍 Geographic Analysis")
    
    if not geographic_analytics.has_geo_data:
        st.warning("⚠️ No geographic data found in the dataset")
        st.info("To enable geographic analysis, ensure your data includes columns: country, region, and/or city")
        return
    
    # Geographic Coverage Overview
    st.subheader("📍 Geographic Coverage")
    coverage = geographic_analytics.get_geographic_coverage()
    
    if 'countries' in coverage:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f'<div class="executive-metric"><h3>{coverage["countries"]["total"]}</h3><p>Countries</p></div>', unsafe_allow_html=True)
        
        if 'regions' in coverage:
            with col2:
                st.markdown(f'<div class="executive-metric"><h3>{coverage["regions"]["total"]}</h3><p>Regions</p></div>', unsafe_allow_html=True)
        
        if 'cities' in coverage:
            with col3:
                st.markdown(f'<div class="executive-metric"><h3>{coverage["cities"]["total"]}</h3><p>Cities</p></div>', unsafe_allow_html=True)
    
    # Regional Performance Analysis
    st.subheader("📊 Regional Performance")
    performance = geographic_analytics.get_regional_performance()
    
    if not performance.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("💰 Revenue by Region")
            fig = px.bar(performance.head(10), 
                        x='total_revenue', 
                        y=performance.columns[0],
                        orientation='h',
                        title="Top 10 Regions by Revenue",
                        color='performance_tier',
                        color_discrete_map={
                            'Dominant': '#28a745',
                            'Strong': '#17a2b8', 
                            'Growing': '#ffc107',
                            'Emerging': '#fd7e14'
                        })
            fig.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("👥 Customer Distribution")
            fig = px.pie(performance.head(8), 
                        values='unique_customers', 
                        names=performance.columns[0],
                        title="Customer Distribution by Region")
            st.plotly_chart(fig, use_container_width=True)
    
    # Market Share Analysis
    if not performance.empty:
        st.subheader("📈 Market Share Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.treemap(performance, 
                           path=[performance.columns[0]], 
                           values='market_share',
                           title="Market Share by Region",
                           color='performance_tier',
                           color_discrete_map={
                               'Dominant': '#28a745',
                               'Strong': '#17a2b8', 
                               'Growing': '#ffc107',
                               'Emerging': '#fd7e14'
                           })
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("💎 Customer Value by Region")
            fig = px.scatter(performance, 
                           x='unique_customers', 
                           y='revenue_per_customer',
                           size='total_revenue',
                           hover_name=performance.columns[0],
                           title="Customer Value vs Customer Count",
                           color='performance_tier',
                           color_discrete_map={
                               'Dominant': '#28a745',
                               'Strong': '#17a2b8', 
                               'Growing': '#ffc107',
                               'Emerging': '#fd7e14'
                           })
            st.plotly_chart(fig, use_container_width=True)
    
    # Geographic Insights and Recommendations
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔍 Geographic Insights")
        insights = geographic_analytics.get_geographic_insights()
        for insight in insights:
            st.markdown(f"• {insight}")
    
    with col2:
        st.subheader("💡 Market Recommendations")
        penetration = geographic_analytics.get_market_penetration_analysis()
        
        if 'expansion_opportunities' in penetration:
            st.markdown("**🚀 Expansion Opportunities:**")
            for market in penetration['expansion_opportunities']:
                st.markdown(f"• {market}")
        
        if 'mature_markets' in penetration:
            st.markdown("**🎯 Mature Markets:**")
            for market in penetration['mature_markets']:
                st.markdown(f"• {market}")
        
        if 'market_concentration' in penetration:
            concentration = penetration['market_concentration']
            st.markdown(f"**📊 Market Concentration:** {concentration['interpretation']}")
    
    # Regional Performance Table
    if not performance.empty:
        st.subheader("📋 Detailed Regional Performance")
        st.dataframe(performance, use_container_width=True)

def show_advanced_analytics(customer_analytics, sales_analytics):
    st.header("🔬 Advanced Analytics")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Cohort Analysis", "Churn Prediction", "Market Basket Analysis", 
        "Customer Journey", "Predictive Insights"
    ])
    
    with tab1:
        st.subheader("👥 Cohort Analysis & Retention Insights")
        cohort_data = customer_analytics.cohort_analysis()
        
        if cohort_data and 'retention_table' in cohort_data:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Retention Heatmap")
                retention_table = cohort_data['retention_table']
                fig = px.imshow(retention_table, 
                               title="Customer Retention by Cohort",
                               color_continuous_scale="Blues",
                               aspect="auto")
                fig.update_layout(
                    xaxis_title="Period Number (Months)",
                    yaxis_title="Cohort Group"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("💰 Revenue per Customer")
                revenue_table = cohort_data['revenue_table']
                fig = px.imshow(revenue_table,
                               title="Revenue per Customer by Cohort",
                               color_continuous_scale="Greens",
                               aspect="auto")
                fig.update_layout(
                    xaxis_title="Period Number (Months)", 
                    yaxis_title="Cohort Group"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Retention insights
            if 'retention_insights' in cohort_data:
                st.subheader("🔍 Retention Insights")
                insights = cohort_data['retention_insights']
                
                col1, col2, col3 = st.columns(3)
                
                if 'retention_milestones' in insights:
                    milestones = insights['retention_milestones']
                    with col1:
                        st.markdown(f'<div class="executive-metric"><h3>{milestones.get("1_month", 0)*100:.1f}%</h3><p>1-Month Retention</p></div>', unsafe_allow_html=True)
                    with col2:
                        st.markdown(f'<div class="executive-metric"><h3>{milestones.get("3_months", 0)*100:.1f}%</h3><p>3-Month Retention</p></div>', unsafe_allow_html=True)
                    with col3:
                        st.markdown(f'<div class="executive-metric"><h3>{milestones.get("6_months", 0)*100:.1f}%</h3><p>6-Month Retention</p></div>', unsafe_allow_html=True)
            
            # Cohort performance table
            if 'cohort_performance' in cohort_data:
                st.subheader("📋 Cohort Performance Summary")
                perf_df = pd.DataFrame(cohort_data['cohort_performance']).T
                st.dataframe(perf_df, use_container_width=True)
        else:
            st.info("Insufficient data for cohort analysis")
    
    with tab2:
        st.subheader("⚠️ Advanced Churn Prediction")
        churn_risk = customer_analytics.identify_churn_risk()
        
        if not churn_risk.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🎯 Churn Risk Distribution")
                risk_counts = churn_risk['risk_level'].value_counts()
                fig = px.pie(values=risk_counts.values, names=risk_counts.index,
                            title="Customer Risk Levels",
                            color_discrete_map={
                                'Low': '#28a745', 'Medium': '#ffc107',
                                'High': '#fd7e14', 'Critical': '#dc3545'
                            })
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("📈 Churn Score Distribution")
                fig = px.histogram(churn_risk, x='churn_score',
                                  title="Churn Score Distribution",
                                  nbins=20, color_discrete_sequence=['#1f77b4'])
                st.plotly_chart(fig, use_container_width=True)
            
            # Risk level metrics
            st.subheader("🚨 Risk Level Summary")
            risk_summary = churn_risk.groupby('risk_level').agg({
                'customer_id': 'count',
                'churn_probability': 'mean',
                'monetary': 'sum'
            }).round(3)
            risk_summary.columns = ['Customer Count', 'Avg Churn Probability', 'Total Revenue at Risk']
            st.dataframe(risk_summary, use_container_width=True)
            
            # High-risk customers
            st.subheader("🔴 High-Risk Customers (Action Required)")
            high_risk = churn_risk[churn_risk['risk_level'].isin(['High', 'Critical'])].head(15)
            st.dataframe(high_risk[['customer_id', 'churn_probability', 'risk_level', 'retention_strategy']], 
                        use_container_width=True)
        else:
            st.info("No churn risk data available")
    
    with tab3:
        st.subheader("🛒 Market Basket Analysis")
        basket_analysis = customer_analytics.market_basket_analysis()
        
        if basket_analysis and 'association_rules' in basket_analysis:
            rules = basket_analysis['association_rules']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🔗 Top Association Rules")
                if rules:
                    rules_df = pd.DataFrame(rules)
                    st.dataframe(rules_df.head(10), use_container_width=True)
                else:
                    st.info("No significant association rules found")
            
            with col2:
                st.subheader("⭐ Product Popularity")
                if 'product_popularity' in basket_analysis:
                    popularity = basket_analysis['product_popularity']
                    top_products = dict(list(popularity.items())[:10])
                    
                    fig = px.bar(x=list(top_products.values()), 
                                y=list(top_products.keys()),
                                orientation='h',
                                title="Most Frequently Purchased Products")
                    fig.update_layout(yaxis={'categoryorder':'total ascending'})
                    st.plotly_chart(fig, use_container_width=True)
            
            # Product affinity heatmap
            if 'affinity_matrix' in basket_analysis:
                st.subheader("🔥 Product Affinity Matrix")
                affinity_matrix = basket_analysis['affinity_matrix']
                
                # Show top products only to avoid clutter
                top_products = list(basket_analysis['product_popularity'].keys())[:10]
                if len(top_products) > 1:
                    matrix_subset = affinity_matrix.loc[top_products, top_products]
                    fig = px.imshow(matrix_subset,
                                   title="Product Purchase Affinity (Top 10 Products)",
                                   color_continuous_scale="Reds")
                    st.plotly_chart(fig, use_container_width=True)
            
            # Customer recommendation demo
            st.subheader("🎯 Recommendation Engine Demo")
            if 'recommendation_engine' in basket_analysis:
                customer_ids = customer_analytics.df['customer_id'].unique()[:20]
                selected_customer = st.selectbox("Select Customer for Recommendations:", customer_ids)
                
                if st.button("Get Recommendations"):
                    recommendations = basket_analysis['recommendation_engine'](selected_customer, top_n=5)
                    if recommendations:
                        st.write(f"**Recommended products for {selected_customer}:**")
                        for i, product in enumerate(recommendations, 1):
                            st.write(f"{i}. {product}")
                    else:
                        st.info("No recommendations available for this customer")
        else:
            st.info("Insufficient transaction data for market basket analysis")
    
    with tab4:
        st.subheader("🗺️ Customer Journey Mapping")
        journey_data = customer_analytics.customer_journey_mapping()
        
        if journey_data and 'stage_distribution' in journey_data:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🎭 Customer Stage Distribution")
                stage_dist = journey_data['stage_distribution']
                fig = px.pie(values=list(stage_dist.values()), 
                            names=list(stage_dist.keys()),
                            title="Customer Lifecycle Stages")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("📊 Journey Patterns")
                if 'journey_patterns' in journey_data:
                    patterns = journey_data['journey_patterns']
                    pattern_df = pd.DataFrame(list(patterns.items()), 
                                            columns=['Pattern', 'Count'])
                    fig = px.bar(pattern_df, x='Count', y='Pattern', 
                                orientation='h',
                                title="Common Customer Journey Patterns")
                    fig.update_layout(yaxis={'categoryorder':'total ascending'})
                    st.plotly_chart(fig, use_container_width=True)
            
            # Stage metrics
            if 'stage_metrics' in journey_data:
                st.subheader("📈 Stage Performance Metrics")
                stage_metrics_df = pd.DataFrame(journey_data['stage_metrics']).T
                st.dataframe(stage_metrics_df, use_container_width=True)
            
            # Conversion metrics
            if 'conversion_metrics' in journey_data:
                st.subheader("🔄 Conversion Metrics")
                conv_metrics = journey_data['conversion_metrics']
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown(f'<div class="executive-metric"><h3>{conv_metrics.get("new_to_repeat_rate", 0):.1f}%</h3><p>New to Repeat Rate</p></div>', unsafe_allow_html=True)
                with col2:
                    st.markdown(f'<div class="executive-metric"><h3>{conv_metrics.get("repeat_to_loyal_rate", 0):.1f}%</h3><p>Repeat to Loyal Rate</p></div>', unsafe_allow_html=True)
                with col3:
                    st.markdown(f'<div class="executive-metric"><h3>{conv_metrics.get("one_time_customer_rate", 0):.1f}%</h3><p>One-time Customer Rate</p></div>', unsafe_allow_html=True)
                with col4:
                    st.markdown(f'<div class="executive-metric"><h3>{conv_metrics.get("customer_lifecycle_ratio", 0):.2f}</h3><p>Lifecycle Ratio</p></div>', unsafe_allow_html=True)
            
            # Journey insights
            if 'insights' in journey_data:
                st.subheader("💡 Journey Insights")
                for insight in journey_data['insights']:
                    st.markdown(f"• {insight}")
        else:
            st.info("Insufficient data for customer journey mapping")
    
    with tab5:
        st.subheader("🔮 Predictive Insights")
        insights = customer_analytics.get_predictive_insights()
        
        st.subheader("🎯 Business Intelligence")
        for insight in insights:
            st.markdown(f"• {insight}")
        
        # Additional predictive metrics
        st.subheader("📊 Advanced Metrics")
        
        try:
            clv_data = customer_analytics.calculate_customer_lifetime_value()
            if not clv_data.empty:
                col1, col2 = st.columns(2)
                
                with col1:
                    avg_clv = clv_data['clv'].mean()
                    median_clv = clv_data['clv'].median()
                    st.markdown(f'<div class="executive-metric"><h3>${avg_clv:.2f}</h3><p>Average Customer Lifetime Value</p></div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="executive-metric"><h3>${median_clv:.2f}</h3><p>Median Customer Lifetime Value</p></div>', unsafe_allow_html=True)
                
                with col2:
                    st.subheader("💎 CLV Distribution by Segment")
                    clv_by_segment = clv_data.groupby('clv_segment')['clv'].mean()
                    fig = px.bar(x=clv_by_segment.index, y=clv_by_segment.values,
                               title="Average CLV by Segment",
                               color=clv_by_segment.values,
                               color_continuous_scale="viridis")
                    st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.info("CLV analysis not available with current data")

def show_sample_data_info():
    st.header("📋 Sample Data Format")
    st.info("Your CSV file should contain the following columns:")
    
    sample_data = pd.DataFrame({
        'customer_id': ['C001', 'C002', 'C001'],
        'order_date': ['2024-01-15', '2024-01-16', '2024-02-01'],
        'product_name': ['Product A', 'Product B', 'Product C'],
        'quantity': [2, 1, 3],
        'unit_price': [25.99, 45.00, 15.50],
        'total_amount': [51.98, 45.00, 46.50]
    })
    
    st.dataframe(sample_data, use_container_width=True)
    
    st.markdown("""
    **Required Columns:**
    - `customer_id`: Unique identifier for each customer
    - `order_date`: Date of the order (YYYY-MM-DD format)
    - `product_name`: Name of the purchased product
    - `quantity`: Number of items purchased
    - `unit_price`: Price per unit
    - `total_amount`: Total amount for the order
    
    **Optional Columns (for Geographic Analysis):**
    - `country`: Customer's country
    - `region`: Customer's region/state
    - `city`: Customer's city
    """)

if __name__ == "__main__":
    main()