import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
import streamlit as st

class SalesAnalytics:
    """
    Sales performance analytics module for tracking revenue trends,
    product performance, and business metrics.
    """
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.df['month_year'] = self.df['order_date'].dt.to_period('M')
        
    def get_sales_metrics(self) -> Dict[str, float]:
        """
        Calculate key sales performance metrics.
        
        Returns:
            dict: Key sales metrics
        """
        try:
            metrics = {}
            
            total_revenue = self.df['total_amount'].sum()
            total_customers = self.df['customer_id'].nunique()
            total_orders = len(self.df)
            
            metrics['total_revenue'] = total_revenue
            metrics['total_customers'] = total_customers
            metrics['total_orders'] = total_orders
            metrics['avg_order_value'] = self.df['total_amount'].mean()
            metrics['revenue_per_customer'] = total_revenue / total_customers if total_customers > 0 else 0
            
            customer_order_counts = self.df.groupby('customer_id').size()
            repeat_customers = (customer_order_counts > 1).sum()
            metrics['repeat_customer_rate'] = (repeat_customers / total_customers) * 100 if total_customers > 0 else 0
            metrics['avg_order_frequency'] = customer_order_counts.mean()
            
            monthly_revenue = self.df.groupby('month_year')['total_amount'].sum()
            if len(monthly_revenue) >= 2:
                current_month = monthly_revenue.iloc[-1]
                previous_month = monthly_revenue.iloc[-2]
                metrics['growth_rate'] = ((current_month - previous_month) / previous_month) * 100 if previous_month > 0 else 0
            else:
                metrics['growth_rate'] = 0
            
            daily_revenue = self.df.groupby(self.df['order_date'].dt.date)['total_amount'].sum()
            metrics['revenue_volatility'] = daily_revenue.std()
            
            top_customers_revenue = self.df.groupby('customer_id')['total_amount'].sum().nlargest(10).sum()
            metrics['top_customers_revenue_share'] = (top_customers_revenue / total_revenue) * 100 if total_revenue > 0 else 0
            
            return metrics
            
        except Exception as e:
            st.error(f"Error calculating sales metrics: {str(e)}")
            return {}
    
    def get_monthly_trends(self) -> pd.DataFrame:
        """
        Calculate monthly sales trends including revenue and customer metrics.
        
        Returns:
            pd.DataFrame: Monthly trend data
        """
        try:
            monthly_data = self.df.groupby('month_year').agg({
                'total_amount': ['sum', 'mean', 'count'],
                'customer_id': 'nunique',
                'quantity': 'sum'
            }).round(2)
            
            monthly_data.columns = ['revenue', 'avg_order_value', 'orders', 'customers', 'units_sold']
            monthly_data.reset_index(inplace=True)
            monthly_data['month_year'] = monthly_data['month_year'].astype(str)
            
            monthly_data['revenue_growth'] = monthly_data['revenue'].pct_change() * 100
            monthly_data['customer_growth'] = monthly_data['customers'].pct_change() * 100
            monthly_data['revenue_per_customer'] = monthly_data['revenue'] / monthly_data['customers']
            
            monthly_data['moving_avg_revenue'] = monthly_data['revenue'].rolling(window=3, min_periods=1).mean()
            
            return monthly_data.set_index('month_year')
            
        except Exception as e:
            st.error(f"Error calculating monthly trends: {str(e)}")
            return pd.DataFrame()
    
    def get_product_performance(self) -> pd.DataFrame:
        """
        Analyze product performance metrics.
        
        Returns:
            pd.DataFrame: Product performance data
        """
        try:
            product_data = self.df.groupby('product_name').agg({
                'total_amount': ['sum', 'mean', 'count'],
                'quantity': 'sum',
                'customer_id': 'nunique'
            }).round(2)
            
            product_data.columns = ['revenue', 'avg_order_value', 'orders', 'units_sold', 'unique_customers']
            product_data.reset_index(inplace=True)
            
            total_revenue = product_data['revenue'].sum()
            product_data['revenue_share'] = (product_data['revenue'] / total_revenue) * 100
            
            product_data['revenue_per_customer'] = product_data['revenue'] / product_data['unique_customers']
            product_data['avg_units_per_order'] = product_data['units_sold'] / product_data['orders']
            
            product_data = product_data.sort_values('revenue', ascending=False)
            
            product_data['rank'] = range(1, len(product_data) + 1)
            product_data['cumulative_revenue_share'] = product_data['revenue_share'].cumsum()
            
            return product_data
            
        except Exception as e:
            st.error(f"Error calculating product performance: {str(e)}")
            return pd.DataFrame()
    
    def get_seasonal_analysis(self) -> Dict[str, Any]:
        """
        Perform seasonal sales analysis.
        
        Returns:
            dict: Seasonal analysis results
        """
        try:
            seasonal_data = {}
            
            monthly_sales = self.df.groupby(self.df['order_date'].dt.month)['total_amount'].sum()
            seasonal_data['monthly_sales'] = monthly_sales
            seasonal_data['peak_month'] = monthly_sales.idxmax()
            seasonal_data['low_month'] = monthly_sales.idxmin()
            
            quarterly_sales = self.df.groupby(self.df['order_date'].dt.quarter)['total_amount'].sum()
            seasonal_data['quarterly_sales'] = quarterly_sales
            seasonal_data['peak_quarter'] = quarterly_sales.idxmax()
            
            weekly_sales = self.df.groupby(self.df['order_date'].dt.dayofweek)['total_amount'].sum()
            day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            weekly_sales.index = [day_names[i] for i in weekly_sales.index]
            seasonal_data['weekly_sales'] = weekly_sales
            seasonal_data['peak_day'] = weekly_sales.idxmax()
            
            seasonal_data['seasonality_strength'] = monthly_sales.std() / monthly_sales.mean()
            
            return seasonal_data
            
        except Exception as e:
            st.error(f"Error in seasonal analysis: {str(e)}")
            return {}
    
    def get_customer_acquisition_trends(self) -> pd.DataFrame:
        """
        Analyze customer acquisition trends over time.
        
        Returns:
            pd.DataFrame: Customer acquisition data
        """
        try:
            first_purchases = self.df.groupby('customer_id')['order_date'].min().reset_index()
            first_purchases.columns = ['customer_id', 'first_purchase_date']
            
            acquisition_trends = first_purchases.groupby(
                first_purchases['first_purchase_date'].dt.to_period('M')
            ).size().reset_index()
            acquisition_trends.columns = ['month', 'new_customers']
            
            acquisition_trends['month'] = acquisition_trends['month'].astype(str)
            acquisition_trends['cumulative_customers'] = acquisition_trends['new_customers'].cumsum()
            acquisition_trends['growth_rate'] = acquisition_trends['new_customers'].pct_change() * 100
            
            acquisition_trends['moving_avg'] = acquisition_trends['new_customers'].rolling(window=3, min_periods=1).mean()
            
            return acquisition_trends.set_index('month')
            
        except Exception as e:
            st.error(f"Error calculating acquisition trends: {str(e)}")
            return pd.DataFrame()
    
    def analyze_pricing_impact(self) -> Dict[str, Any]:
        """
        Analyze the impact of pricing on sales performance.
        
        Returns:
            dict: Pricing analysis results
        """
        try:
            pricing_data = {}
            
            price_ranges = pd.cut(self.df['unit_price'], bins=5, labels=['Very Low', 'Low', 'Medium', 'High', 'Very High'])
            price_analysis = self.df.groupby(price_ranges).agg({
                'quantity': 'sum',
                'total_amount': 'sum',
                'customer_id': 'nunique'
            })
            
            pricing_data['price_range_performance'] = price_analysis
            
            product_price_elasticity = {}
            for product in self.df['product_name'].unique():
                product_data = self.df[self.df['product_name'] == product]
                if len(product_data) > 5:
                    correlation = np.corrcoef(product_data['unit_price'], product_data['quantity'])[0,1]
                    product_price_elasticity[product] = correlation
            
            pricing_data['price_elasticity'] = product_price_elasticity
            
            avg_price_by_month = self.df.groupby('month_year')['unit_price'].mean()
            sales_by_month = self.df.groupby('month_year')['quantity'].sum()
            pricing_data['price_sales_correlation'] = np.corrcoef(avg_price_by_month, sales_by_month)[0,1] if len(avg_price_by_month) > 1 else 0
            
            return pricing_data
            
        except Exception as e:
            st.error(f"Error in pricing analysis: {str(e)}")
            return {}
    
    def get_top_customers(self, n: int = 20) -> pd.DataFrame:
        """
        Identify top customers by various metrics.
        
        Args:
            n: Number of top customers to return
            
        Returns:
            pd.DataFrame: Top customer data
        """
        try:
            customer_summary = self.df.groupby('customer_id').agg({
                'total_amount': ['sum', 'mean', 'count'],
                'order_date': ['min', 'max'],
                'quantity': 'sum'
            }).round(2)
            
            customer_summary.columns = ['total_spent', 'avg_order_value', 'order_count', 'first_order', 'last_order', 'total_quantity']
            customer_summary.reset_index(inplace=True)
            
            customer_summary['customer_lifespan'] = (customer_summary['last_order'] - customer_summary['first_order']).dt.days
            customer_summary['days_since_last_order'] = (self.df['order_date'].max() - customer_summary['last_order']).dt.days
            
            customer_summary['order_frequency'] = customer_summary['order_count'] / (customer_summary['customer_lifespan'] + 1) * 365
            customer_summary['order_frequency'] = customer_summary['order_frequency'].fillna(customer_summary['order_count'])
            
            top_by_revenue = customer_summary.nlargest(n, 'total_spent').copy()
            top_by_revenue['rank_type'] = 'Revenue'
            
            top_by_frequency = customer_summary.nlargest(n, 'order_count').copy()
            top_by_frequency['rank_type'] = 'Frequency'
            
            top_by_recency = customer_summary.nsmallest(n, 'days_since_last_order').copy()
            top_by_recency['rank_type'] = 'Recency'
            
            return pd.concat([top_by_revenue, top_by_frequency, top_by_recency]).drop_duplicates()
            
        except Exception as e:
            st.error(f"Error identifying top customers: {str(e)}")
            return pd.DataFrame()
    
    def forecast_revenue(self, periods: int = 3) -> Dict[str, Any]:
        """
        Simple revenue forecasting based on trends.
        
        Args:
            periods: Number of periods to forecast
            
        Returns:
            dict: Forecast results
        """
        try:
            monthly_revenue = self.df.groupby('month_year')['total_amount'].sum()
            
            if len(monthly_revenue) < 3:
                return {"error": "Insufficient data for forecasting"}
            
            recent_months = monthly_revenue.tail(3)
            growth_rate = recent_months.pct_change().mean()
            
            last_month_revenue = monthly_revenue.iloc[-1]
            
            forecast = []
            current_revenue = last_month_revenue
            
            for i in range(periods):
                current_revenue = current_revenue * (1 + growth_rate)
                forecast.append(current_revenue)
            
            forecast_data = {
                'forecast': forecast,
                'growth_rate': growth_rate * 100,
                'confidence': 'Low' if abs(growth_rate) > 0.5 else 'Medium' if abs(growth_rate) > 0.2 else 'High'
            }
            
            return forecast_data
            
        except Exception as e:
            st.error(f"Error in revenue forecasting: {str(e)}")
            return {"error": str(e)}