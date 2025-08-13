import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

from modules.data_processor import DataProcessor
from modules.customer_analytics import CustomerAnalytics
from modules.sales_analytics import SalesAnalytics

st.set_page_config(
    page_title="Customer Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_custom_css():
    st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        max-width: none;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #1f77b4;
    }
    .segment-high { border-left-color: #28a745; }
    .segment-medium { border-left-color: #ffc107; }
    .segment-low { border-left-color: #dc3545; }
    
    .stSelectbox > div > div > div > div {
        background-color: white;
    }
    
    h1 {
        color: #1f77b4;
        font-family: 'Arial', sans-serif;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 10px;
    }
    
    .dashboard-header {
        background: linear-gradient(90deg, #1f77b4 0%, #17a2b8 100%);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    load_custom_css()
    
    st.markdown('<div class="dashboard-header"><h1>🎯 Customer Analytics Dashboard</h1><p>Advanced e-commerce customer intelligence platform</p></div>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.header("📂 Data Upload")
        uploaded_file = st.file_uploader(
            "Upload Customer Transaction Data",
            type=['csv'],
            help="Upload CSV file with customer transaction data"
        )
        
        if uploaded_file is not None:
            try:
                processor = DataProcessor()
                df = processor.load_and_validate_data(uploaded_file)
                
                if df is not None:
                    st.success(f"✅ Data loaded: {len(df):,} records")
                    
                    st.header("🔧 Analysis Options")
                    analysis_type = st.selectbox(
                        "Select Analysis",
                        ["Overview", "Customer Segmentation", "Sales Performance", "Advanced Analytics"]
                    )
                    
                    date_range = st.date_input(
                        "Date Range",
                        value=(df['order_date'].min().date(), df['order_date'].max().date()),
                        min_value=df['order_date'].min().date(),
                        max_value=df['order_date'].max().date()
                    )
                    
                    if len(date_range) == 2:
                        start_date, end_date = date_range
                        mask = (df['order_date'].dt.date >= start_date) & (df['order_date'].dt.date <= end_date)
                        filtered_df = df[mask].copy()
                        
                        customer_analytics = CustomerAnalytics(filtered_df)
                        sales_analytics = SalesAnalytics(filtered_df)
                        
                        if analysis_type == "Overview":
                            show_overview(filtered_df, customer_analytics, sales_analytics)
                        elif analysis_type == "Customer Segmentation":
                            show_customer_segmentation(customer_analytics)
                        elif analysis_type == "Sales Performance":
                            show_sales_performance(sales_analytics)
                        elif analysis_type == "Advanced Analytics":
                            show_advanced_analytics(customer_analytics, sales_analytics)
                            
            except Exception as e:
                st.error(f"❌ Error loading data: {str(e)}")
                st.info("Please ensure your CSV has the required columns: customer_id, order_date, product_name, quantity, unit_price, total_amount")
    else:
        st.info("👆 Please upload a CSV file to begin analysis")
        show_sample_data_info()

def show_overview(df, customer_analytics, sales_analytics):
    st.header("📊 Business Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_revenue = df['total_amount'].sum()
        st.markdown(f'<div class="metric-container"><h3>${total_revenue:,.0f}</h3><p>Total Revenue</p></div>', unsafe_allow_html=True)
    
    with col2:
        total_customers = df['customer_id'].nunique()
        st.markdown(f'<div class="metric-container"><h3>{total_customers:,}</h3><p>Total Customers</p></div>', unsafe_allow_html=True)
    
    with col3:
        total_orders = len(df)
        st.markdown(f'<div class="metric-container"><h3>{total_orders:,}</h3><p>Total Orders</p></div>', unsafe_allow_html=True)
    
    with col4:
        avg_order_value = df['total_amount'].mean()
        st.markdown(f'<div class="metric-container"><h3>${avg_order_value:.2f}</h3><p>Avg Order Value</p></div>', unsafe_allow_html=True)
    
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
            color_class = 'segment-high' if segment in ['Champions', 'Loyal Customers'] else 'segment-medium' if segment == 'Potential Loyalists' else 'segment-low'
            st.markdown(f'''
            <div class="metric-container {color_class}">
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
        st.markdown(f'<div class="metric-container"><h3>{metrics["growth_rate"]:.1f}%</h3><p>Revenue Growth</p></div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'<div class="metric-container"><h3>{metrics["repeat_customer_rate"]:.1f}%</h3><p>Repeat Customer Rate</p></div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'<div class="metric-container"><h3>{metrics["avg_order_frequency"]:.1f}</h3><p>Avg Order Frequency</p></div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown(f'<div class="metric-container"><h3>${metrics["revenue_per_customer"]:.2f}</h3><p>Revenue per Customer</p></div>', unsafe_allow_html=True)
    
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
        fig.update_yaxis(title_text="Revenue ($)", secondary_y=False)
        fig.update_yaxis(title_text="Customers", secondary_y=True)
        fig.update_layout(title="Monthly Revenue & Customer Trends")
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🛒 Product Performance")
        product_data = sales_analytics.get_product_performance()
        
        fig = px.treemap(product_data, path=['product_name'], values='revenue',
                        title="Product Revenue Treemap")
        st.plotly_chart(fig, use_container_width=True)

def show_advanced_analytics(customer_analytics, sales_analytics):
    st.header("🔬 Advanced Analytics")
    
    tab1, tab2, tab3 = st.tabs(["Cohort Analysis", "Predictive Insights", "Churn Analysis"])
    
    with tab1:
        st.subheader("👥 Cohort Analysis")
        cohort_data = customer_analytics.cohort_analysis()
        
        if not cohort_data.empty:
            fig = px.imshow(cohort_data, 
                           title="Customer Retention Cohort Analysis",
                           color_continuous_scale="Blues")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Insufficient data for cohort analysis")
    
    with tab2:
        st.subheader("🔮 Predictive Insights")
        insights = customer_analytics.get_predictive_insights()
        
        for insight in insights:
            st.markdown(f"• {insight}")
    
    with tab3:
        st.subheader("⚠️ Churn Risk Analysis")
        churn_risk = customer_analytics.identify_churn_risk()
        
        if not churn_risk.empty:
            fig = px.histogram(churn_risk, x='risk_level', 
                              title="Customer Churn Risk Distribution")
            st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(churn_risk.head(20), use_container_width=True)

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
    **Column Requirements:**
    - `customer_id`: Unique identifier for each customer
    - `order_date`: Date of the order (YYYY-MM-DD format)
    - `product_name`: Name of the purchased product
    - `quantity`: Number of items purchased
    - `unit_price`: Price per unit
    - `total_amount`: Total amount for the order
    """)

if __name__ == "__main__":
    main()