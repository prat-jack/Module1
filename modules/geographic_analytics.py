import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional
import streamlit as st

class GeographicAnalytics:
    """
    Geographic analytics module for analyzing customer and sales data by location.
    Provides regional performance metrics, geographic segmentation, and actionable insights.
    """
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.has_geo_data = self._validate_geographic_data()
        
    def _validate_geographic_data(self) -> bool:
        """Check if the dataset contains geographic columns."""
        geo_columns = ['country', 'region', 'city']
        available_geo_cols = [col for col in geo_columns if col in self.df.columns]
        return len(available_geo_cols) > 0
    
    def get_geographic_coverage(self) -> Dict[str, Any]:
        """
        Analyze geographic coverage of the customer base.
        
        Returns:
            dict: Geographic coverage statistics
        """
        if not self.has_geo_data:
            return {"error": "No geographic data available"}
        
        coverage = {}
        
        if 'country' in self.df.columns:
            coverage['countries'] = {
                'total': self.df['country'].nunique(),
                'list': self.df['country'].value_counts().to_dict(),
                'top_country': self.df['country'].value_counts().index[0]
            }
        
        if 'region' in self.df.columns:
            coverage['regions'] = {
                'total': self.df['region'].nunique(),
                'list': self.df['region'].value_counts().to_dict(),
                'top_region': self.df['region'].value_counts().index[0]
            }
        
        if 'city' in self.df.columns:
            coverage['cities'] = {
                'total': self.df['city'].nunique(),
                'list': self.df['city'].value_counts().head(20).to_dict(),
                'top_city': self.df['city'].value_counts().index[0]
            }
        
        return coverage
    
    def get_regional_performance(self) -> pd.DataFrame:
        """
        Calculate performance metrics by geographic region.
        
        Returns:
            pd.DataFrame: Regional performance metrics
        """
        if not self.has_geo_data:
            return pd.DataFrame()
        
        try:
            # Determine the primary geographic level to analyze
            geo_level = 'country' if 'country' in self.df.columns else 'region' if 'region' in self.df.columns else 'city'
            
            regional_stats = self.df.groupby(geo_level).agg({
                'total_amount': ['sum', 'mean', 'count'],
                'customer_id': 'nunique',
                'quantity': 'sum'
            }).round(2)
            
            regional_stats.columns = ['total_revenue', 'avg_order_value', 'total_orders', 'unique_customers', 'units_sold']
            regional_stats.reset_index(inplace=True)
            
            # Calculate derived metrics
            regional_stats['revenue_per_customer'] = regional_stats['total_revenue'] / regional_stats['unique_customers']
            regional_stats['orders_per_customer'] = regional_stats['total_orders'] / regional_stats['unique_customers']
            
            # Calculate market share
            total_revenue = regional_stats['total_revenue'].sum()
            regional_stats['market_share'] = (regional_stats['total_revenue'] / total_revenue * 100).round(2)
            
            # Rank regions
            regional_stats = regional_stats.sort_values('total_revenue', ascending=False)
            regional_stats['revenue_rank'] = range(1, len(regional_stats) + 1)
            
            # Performance classification
            regional_stats['performance_tier'] = pd.cut(
                regional_stats['market_share'], 
                bins=[0, 5, 15, 30, 100], 
                labels=['Emerging', 'Growing', 'Strong', 'Dominant']
            )
            
            return regional_stats
            
        except Exception as e:
            st.error(f"Error in regional performance analysis: {str(e)}")
            return pd.DataFrame()
    
    def get_geographic_customer_segments(self) -> Dict[str, pd.DataFrame]:
        """
        Create customer segments based on geographic and behavioral data.
        
        Returns:
            dict: Geographic customer segments
        """
        if not self.has_geo_data:
            return {}
        
        try:
            segments = {}
            
            # Customer metrics by location
            if 'country' in self.df.columns:
                country_customers = self.df.groupby(['country', 'customer_id']).agg({
                    'total_amount': 'sum',
                    'order_date': 'count'
                }).reset_index()
                country_customers.columns = ['country', 'customer_id', 'total_spent', 'order_frequency']
                
                # Segment customers within each country
                for country in country_customers['country'].unique():
                    country_data = country_customers[country_customers['country'] == country].copy()
                    
                    # Create spending segments
                    country_data['spending_segment'] = pd.qcut(
                        country_data['total_spent'].rank(method='first'),
                        q=3, labels=['Low Spender', 'Medium Spender', 'High Spender']
                    )
                    
                    # Create frequency segments
                    country_data['frequency_segment'] = pd.qcut(
                        country_data['order_frequency'].rank(method='first'),
                        q=3, labels=['Occasional', 'Regular', 'Frequent']
                    )
                    
                    segments[country] = country_data
            
            return segments
            
        except Exception as e:
            st.error(f"Error in geographic customer segmentation: {str(e)}")
            return {}
    
    def analyze_geographic_trends(self) -> Dict[str, Any]:
        """
        Analyze trends and patterns across geographic regions.
        
        Returns:
            dict: Geographic trend analysis
        """
        if not self.has_geo_data:
            return {"error": "No geographic data available"}
        
        try:
            trends = {}
            
            # Revenue growth by region over time
            if 'country' in self.df.columns:
                monthly_country_revenue = self.df.groupby([
                    self.df['order_date'].dt.to_period('M'), 'country'
                ])['total_amount'].sum().reset_index()
                
                growth_rates = {}
                for country in monthly_country_revenue['country'].unique():
                    country_data = monthly_country_revenue[monthly_country_revenue['country'] == country]
                    if len(country_data) >= 2:
                        country_data = country_data.sort_values('order_date')
                        growth_rate = country_data['total_amount'].pct_change().mean() * 100
                        growth_rates[country] = round(growth_rate, 2)
                
                trends['country_growth_rates'] = growth_rates
                trends['fastest_growing_country'] = max(growth_rates, key=growth_rates.get) if growth_rates else None
            
            # Product preferences by region
            if 'country' in self.df.columns:
                country_products = self.df.groupby(['country', 'product_name'])['total_amount'].sum().reset_index()
                top_products_by_country = {}
                
                for country in country_products['country'].unique():
                    country_data = country_products[country_products['country'] == country]
                    top_product = country_data.nlargest(1, 'total_amount')['product_name'].iloc[0]
                    top_products_by_country[country] = top_product
                
                trends['top_products_by_country'] = top_products_by_country
            
            # Seasonal patterns by geography
            if 'country' in self.df.columns:
                seasonal_data = self.df.groupby([
                    'country', self.df['order_date'].dt.month
                ])['total_amount'].sum().reset_index()
                
                peak_months_by_country = {}
                for country in seasonal_data['country'].unique():
                    country_seasonal = seasonal_data[seasonal_data['country'] == country]
                    peak_month = country_seasonal.nlargest(1, 'total_amount')['order_date'].iloc[0]
                    peak_months_by_country[country] = peak_month
                
                trends['peak_months_by_country'] = peak_months_by_country
            
            return trends
            
        except Exception as e:
            st.error(f"Error in geographic trend analysis: {str(e)}")
            return {}
    
    def get_market_penetration_analysis(self) -> Dict[str, Any]:
        """
        Analyze market penetration and expansion opportunities.
        
        Returns:
            dict: Market penetration insights
        """
        if not self.has_geo_data:
            return {"error": "No geographic data available"}
        
        try:
            penetration = {}
            
            if 'country' in self.df.columns:
                country_metrics = self.df.groupby('country').agg({
                    'customer_id': 'nunique',
                    'total_amount': 'sum',
                    'order_date': 'count'
                }).reset_index()
                
                country_metrics.columns = ['country', 'customers', 'revenue', 'orders']
                country_metrics['avg_revenue_per_customer'] = country_metrics['revenue'] / country_metrics['customers']
                country_metrics['avg_orders_per_customer'] = country_metrics['orders'] / country_metrics['customers']
                
                # Identify expansion opportunities (low penetration, high value)
                country_metrics['expansion_score'] = (
                    country_metrics['avg_revenue_per_customer'] / country_metrics['customers']
                )
                
                top_expansion = country_metrics.nlargest(3, 'expansion_score')['country'].tolist()
                penetration['expansion_opportunities'] = top_expansion
                
                # Identify mature markets (high penetration, stable revenue)
                mature_markets = country_metrics.nlargest(3, 'customers')['country'].tolist()
                penetration['mature_markets'] = mature_markets
                
                # Calculate market concentration
                total_customers = country_metrics['customers'].sum()
                country_metrics['customer_share'] = country_metrics['customers'] / total_customers * 100
                
                # Herfindahl-Hirschman Index for market concentration
                hhi = (country_metrics['customer_share'] ** 2).sum()
                penetration['market_concentration'] = {
                    'hhi_score': round(hhi, 2),
                    'interpretation': 'Highly Concentrated' if hhi > 2500 else 'Moderately Concentrated' if hhi > 1500 else 'Unconcentrated'
                }
            
            return penetration
            
        except Exception as e:
            st.error(f"Error in market penetration analysis: {str(e)}")
            return {}
    
    def get_geographic_insights(self) -> List[str]:
        """
        Generate actionable business insights based on geographic analysis.
        
        Returns:
            list: List of geographic insights
        """
        if not self.has_geo_data:
            return ["Geographic data not available for analysis"]
        
        insights = []
        
        try:
            # Get performance data
            performance = self.get_regional_performance()
            trends = self.analyze_geographic_trends()
            penetration = self.get_market_penetration_analysis()
            
            if not performance.empty:
                # Revenue concentration insights
                top_region = performance.iloc[0]
                insights.append(f"{top_region.iloc[0]} is your top market with {top_region['market_share']:.1f}% market share and ${top_region['total_revenue']:,.0f} revenue")
                
                # Customer value insights
                if 'revenue_per_customer' in performance.columns:
                    high_value_region = performance.nlargest(1, 'revenue_per_customer').iloc[0]
                    insights.append(f"{high_value_region.iloc[0]} has the highest customer value at ${high_value_region['revenue_per_customer']:.0f} per customer")
            
            # Growth opportunities
            if 'expansion_opportunities' in penetration:
                expansion_markets = penetration['expansion_opportunities'][:2]
                if expansion_markets:
                    insights.append(f"Consider expansion focus on {', '.join(expansion_markets)} - high value, low penetration markets")
            
            # Product localization insights
            if 'top_products_by_country' in trends:
                product_insights = trends['top_products_by_country']
                unique_preferences = len(set(product_insights.values()))
                if unique_preferences > 1:
                    insights.append("Regional product preferences vary - consider localized inventory and marketing strategies")
                else:
                    insights.append("Product preferences are consistent across regions - standardized approach may work well")
            
            # Seasonal insights
            if 'peak_months_by_country' in trends:
                seasonal_insights = trends['peak_months_by_country']
                months = list(seasonal_insights.values())
                if len(set(months)) > 1:
                    insights.append("Peak seasons vary by region - implement region-specific promotional calendars")
            
            # Market concentration insights
            if 'market_concentration' in penetration:
                concentration = penetration['market_concentration']
                if concentration['hhi_score'] > 2500:
                    insights.append("Market is highly concentrated - diversification into new regions recommended")
                elif concentration['hhi_score'] < 1500:
                    insights.append("Market is well-diversified across regions - maintain balanced growth strategy")
            
            # Growth rate insights
            if 'country_growth_rates' in trends and 'fastest_growing_country' in trends:
                fastest_growing = trends['fastest_growing_country']
                if fastest_growing:
                    insights.append(f"{fastest_growing} shows strongest growth momentum - prioritize investment and expansion there")
            
            if len(insights) == 0:
                insights.append("Geographic analysis complete - monitor regional performance trends for optimization opportunities")
            
            return insights[:8]
            
        except Exception as e:
            st.error(f"Error generating geographic insights: {str(e)}")
            return ["Error generating geographic insights"]
    
    def get_location_based_recommendations(self) -> Dict[str, List[str]]:
        """
        Generate location-specific business recommendations.
        
        Returns:
            dict: Recommendations by geographic area
        """
        if not self.has_geo_data:
            return {}
        
        try:
            recommendations = {}
            performance = self.get_regional_performance()
            
            if not performance.empty:
                for _, region_data in performance.iterrows():
                    region_name = region_data.iloc[0]
                    region_recs = []
                    
                    # Performance-based recommendations
                    if region_data['performance_tier'] == 'Dominant':
                        region_recs.append("Maintain market leadership through premium service and customer retention")
                        region_recs.append("Consider this region as a testing ground for new products")
                    elif region_data['performance_tier'] == 'Strong':
                        region_recs.append("Invest in growth initiatives to capture larger market share")
                        region_recs.append("Expand customer acquisition efforts")
                    elif region_data['performance_tier'] == 'Growing':
                        region_recs.append("Focus on customer education and brand awareness")
                        region_recs.append("Optimize pricing strategy for market conditions")
                    else:  # Emerging
                        region_recs.append("Evaluate market potential and entry barriers")
                        region_recs.append("Consider partnerships or local market expertise")
                    
                    # Value-based recommendations
                    if region_data['revenue_per_customer'] > performance['revenue_per_customer'].median():
                        region_recs.append("Leverage high customer value with premium offerings")
                    else:
                        region_recs.append("Develop value-oriented product bundles")
                    
                    recommendations[region_name] = region_recs
            
            return recommendations
            
        except Exception as e:
            st.error(f"Error generating location-based recommendations: {str(e)}")
            return {}