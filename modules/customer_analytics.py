import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
import streamlit as st
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class CustomerAnalytics:
    """
    Advanced customer analytics module for RFM analysis, segmentation, 
    lifetime value calculation, and predictive insights.
    """
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.reference_date = self.df['order_date'].max()
        self.rfm_data = None
        self.segments = None
        
    def calculate_rfm(self) -> pd.DataFrame:
        """
        Calculate RFM (Recency, Frequency, Monetary) metrics for each customer.
        
        Returns:
            pd.DataFrame: RFM analysis results with customer segments
        """
        try:
            customer_data = self.df.groupby('customer_id').agg({
                'order_date': ['max', 'count'],
                'total_amount': ['sum', 'mean']
            }).round(2)
            
            customer_data.columns = ['last_order_date', 'frequency', 'monetary', 'avg_order_value']
            customer_data.reset_index(inplace=True)
            
            customer_data['recency'] = (self.reference_date - customer_data['last_order_date']).dt.days
            
            customer_data['R_score'] = pd.qcut(customer_data['recency'].rank(method='first'), 
                                             q=5, labels=[5,4,3,2,1])
            customer_data['F_score'] = pd.qcut(customer_data['frequency'].rank(method='first'), 
                                             q=5, labels=[1,2,3,4,5])
            customer_data['M_score'] = pd.qcut(customer_data['monetary'].rank(method='first'), 
                                             q=5, labels=[1,2,3,4,5])
            
            customer_data['R_score'] = customer_data['R_score'].astype(int)
            customer_data['F_score'] = customer_data['F_score'].astype(int)
            customer_data['M_score'] = customer_data['M_score'].astype(int)
            
            customer_data['RFM_score'] = (
                customer_data['R_score'].astype(str) + 
                customer_data['F_score'].astype(str) + 
                customer_data['M_score'].astype(str)
            )
            
            customer_data['segment'] = customer_data['RFM_score'].apply(self._categorize_rfm)
            
            self.rfm_data = customer_data
            return customer_data
            
        except Exception as e:
            st.error(f"Error in RFM calculation: {str(e)}")
            return pd.DataFrame()
    
    def _categorize_rfm(self, rfm_score: str) -> str:
        """
        Categorize customers based on RFM scores into business segments.
        
        Args:
            rfm_score: RFM score string (e.g., '555')
            
        Returns:
            str: Customer segment name
        """
        if rfm_score in ['555', '554', '544', '545', '454', '455', '445']:
            return 'Champions'
        elif rfm_score in ['543', '444', '435', '355', '354', '345', '344', '335']:
            return 'Loyal Customers'
        elif rfm_score in ['553', '551', '552', '541', '542', '533', '532', '531', '452', '451']:
            return 'Potential Loyalists'
        elif rfm_score in ['512', '511', '422', '421', '412', '411', '311']:
            return 'New Customers'
        elif rfm_score in ['155', '154', '144', '214', '215', '115', '114']:
            return 'At Risk'
        elif rfm_score in ['155', '254', '245', '253', '244', '243', '234', '343', '334']:
            return 'Cannot Lose Them'
        elif rfm_score in ['231', '241', '251', '233', '232', '223', '222', '231', '241', '251']:
            return 'Hibernating'
        else:
            return 'Lost Customers'
    
    def get_customer_segments(self) -> Dict[str, Dict]:
        """
        Get customer segment summary with counts and revenue.
        
        Returns:
            dict: Segment summary statistics
        """
        if self.rfm_data is None:
            self.calculate_rfm()
        
        if self.rfm_data.empty:
            return {}
        
        segment_summary = {}
        
        for segment in self.rfm_data['segment'].unique():
            segment_customers = self.rfm_data[self.rfm_data['segment'] == segment]
            
            segment_summary[segment] = {
                'count': len(segment_customers),
                'revenue': segment_customers['monetary'].sum(),
                'avg_recency': segment_customers['recency'].mean(),
                'avg_frequency': segment_customers['frequency'].mean(),
                'avg_monetary': segment_customers['monetary'].mean()
            }
        
        self.segments = segment_summary
        return segment_summary
    
    def calculate_customer_lifetime_value(self) -> pd.DataFrame:
        """
        Calculate Customer Lifetime Value (CLV) using historical data.
        
        Returns:
            pd.DataFrame: CLV calculations for each customer
        """
        try:
            customer_metrics = self.df.groupby('customer_id').agg({
                'order_date': ['min', 'max', 'count'],
                'total_amount': ['sum', 'mean']
            }).round(2)
            
            customer_metrics.columns = ['first_order', 'last_order', 'frequency', 'total_revenue', 'avg_order_value']
            customer_metrics.reset_index(inplace=True)
            
            customer_metrics['lifespan_days'] = (customer_metrics['last_order'] - customer_metrics['first_order']).dt.days
            customer_metrics['lifespan_days'] = customer_metrics['lifespan_days'].replace(0, 1)
            
            customer_metrics['purchase_frequency'] = customer_metrics['frequency'] / customer_metrics['lifespan_days'] * 365
            
            avg_lifespan = customer_metrics['lifespan_days'].mean()
            
            customer_metrics['predicted_lifespan'] = np.where(
                customer_metrics['frequency'] > 1,
                customer_metrics['lifespan_days'],
                avg_lifespan
            )
            
            customer_metrics['clv'] = (
                customer_metrics['avg_order_value'] * 
                customer_metrics['purchase_frequency'] * 
                (customer_metrics['predicted_lifespan'] / 365)
            ).round(2)
            
            customer_metrics['clv_segment'] = pd.qcut(
                customer_metrics['clv'].rank(method='first'),
                q=4, labels=['Low', 'Medium', 'High', 'Very High']
            )
            
            return customer_metrics
            
        except Exception as e:
            st.error(f"Error in CLV calculation: {str(e)}")
            return pd.DataFrame()
    
    def cohort_analysis(self) -> pd.DataFrame:
        """
        Perform cohort analysis to understand customer retention.
        
        Returns:
            pd.DataFrame: Cohort analysis results
        """
        try:
            df = self.df.copy()
            
            df['order_period'] = df['order_date'].dt.to_period('M')
            
            cohort = df.groupby('customer_id')['order_date'].min().reset_index()
            cohort.columns = ['customer_id', 'cohort_group']
            cohort['cohort_group'] = cohort['cohort_group'].dt.to_period('M')
            
            df = df.merge(cohort, on='customer_id')
            
            df['period_number'] = (df['order_period'] - df['cohort_group']).apply(lambda x: x.n)
            
            cohort_data = df.groupby(['cohort_group', 'period_number'])['customer_id'].nunique().reset_index()
            cohort_sizes = df.groupby('cohort_group')['customer_id'].nunique().reset_index()
            cohort_table = cohort_data.merge(cohort_sizes, on='cohort_group')
            
            cohort_table['retention_rate'] = cohort_table['customer_id_x'] / cohort_table['customer_id_y']
            
            cohort_table = cohort_table.pivot(index='cohort_group', 
                                            columns='period_number', 
                                            values='retention_rate')
            
            cohort_table.index = cohort_table.index.astype(str)
            
            return cohort_table.round(3)
            
        except Exception as e:
            st.error(f"Error in cohort analysis: {str(e)}")
            return pd.DataFrame()
    
    def identify_churn_risk(self) -> pd.DataFrame:
        """
        Identify customers at risk of churning based on behavioral patterns.
        
        Returns:
            pd.DataFrame: Customers with churn risk scores
        """
        try:
            if self.rfm_data is None:
                self.calculate_rfm()
            
            if self.rfm_data.empty:
                return pd.DataFrame()
            
            churn_data = self.rfm_data.copy()
            
            churn_data['churn_score'] = (
                churn_data['recency'] * 0.4 +
                (6 - churn_data['frequency']) * 10 * 0.3 +
                (6 - churn_data['M_score']) * 10 * 0.3
            )
            
            churn_data['risk_level'] = pd.cut(
                churn_data['churn_score'],
                bins=[0, 20, 40, 60, 100],
                labels=['Low', 'Medium', 'High', 'Critical']
            )
            
            churn_data = churn_data.sort_values('churn_score', ascending=False)
            
            return churn_data[['customer_id', 'recency', 'frequency', 'monetary', 
                             'segment', 'churn_score', 'risk_level']]
            
        except Exception as e:
            st.error(f"Error in churn risk analysis: {str(e)}")
            return pd.DataFrame()
    
    def advanced_segmentation(self, n_clusters: int = 5) -> pd.DataFrame:
        """
        Perform advanced customer segmentation using machine learning clustering.
        
        Args:
            n_clusters: Number of customer segments to create
            
        Returns:
            pd.DataFrame: Advanced segmentation results
        """
        try:
            if self.rfm_data is None:
                self.calculate_rfm()
            
            if self.rfm_data.empty:
                return pd.DataFrame()
            
            features = ['recency', 'frequency', 'monetary']
            X = self.rfm_data[features].copy()
            
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(X_scaled)
            
            result = self.rfm_data.copy()
            result['ml_segment'] = clusters
            
            cluster_summary = result.groupby('ml_segment').agg({
                'recency': 'mean',
                'frequency': 'mean', 
                'monetary': 'mean',
                'customer_id': 'count'
            }).round(2)
            
            cluster_names = {
                0: 'High Value',
                1: 'Regular', 
                2: 'New Customers',
                3: 'At Risk',
                4: 'Low Value'
            }
            
            result['ml_segment_name'] = result['ml_segment'].map(cluster_names)
            
            return result
            
        except Exception as e:
            st.error(f"Error in advanced segmentation: {str(e)}")
            return pd.DataFrame()
    
    def get_predictive_insights(self) -> List[str]:
        """
        Generate predictive insights based on customer analytics.
        
        Returns:
            list: List of predictive insights
        """
        insights = []
        
        try:
            if self.segments is None:
                self.get_customer_segments()
            
            if not self.segments:
                return ["Insufficient data for predictive insights"]
            
            total_customers = sum(segment['count'] for segment in self.segments.values())
            total_revenue = sum(segment['revenue'] for segment in self.segments.values())
            
            champions = self.segments.get('Champions', {'count': 0, 'revenue': 0})
            at_risk = self.segments.get('At Risk', {'count': 0, 'revenue': 0})
            lost = self.segments.get('Lost Customers', {'count': 0, 'revenue': 0})
            
            if champions['count'] > 0:
                champion_percent = (champions['count'] / total_customers) * 100
                insights.append(f"Champion customers represent {champion_percent:.1f}% of your base but generate ${champions['revenue']:,.0f} in revenue")
            
            if at_risk['count'] > 0:
                risk_percent = (at_risk['count'] / total_customers) * 100
                insights.append(f"{risk_percent:.1f}% of customers are at risk of churning, representing potential revenue loss of ${at_risk['revenue']:,.0f}")
            
            if lost['count'] > 0:
                lost_percent = (lost['count'] / total_customers) * 100
                insights.append(f"{lost_percent:.1f}% of customers are already lost, representing ${lost['revenue']:,.0f} in historical value")
            
            avg_order_value = self.df['total_amount'].mean()
            recent_orders = self.df[self.df['order_date'] >= (self.reference_date - timedelta(days=30))]
            
            if not recent_orders.empty:
                recent_aov = recent_orders['total_amount'].mean()
                aov_change = ((recent_aov - avg_order_value) / avg_order_value) * 100
                
                if aov_change > 5:
                    insights.append(f"Average order value has increased by {aov_change:.1f}% in the last 30 days")
                elif aov_change < -5:
                    insights.append(f"Average order value has decreased by {abs(aov_change):.1f}% in the last 30 days - consider promotional strategies")
            
            repeat_customers = len(self.df[self.df.duplicated('customer_id')])
            repeat_rate = (repeat_customers / total_customers) * 100
            
            if repeat_rate < 20:
                insights.append("Low repeat purchase rate detected - focus on customer retention strategies")
            elif repeat_rate > 60:
                insights.append("High customer loyalty detected - leverage this for referral programs")
            
            seasonal_data = self.df.groupby(self.df['order_date'].dt.month)['total_amount'].sum()
            peak_month = seasonal_data.idxmax()
            insights.append(f"Peak sales month is {peak_month} - plan inventory and marketing accordingly")
            
            if len(insights) == 0:
                insights.append("Continue monitoring customer behavior patterns for emerging trends")
            
            return insights[:8]
            
        except Exception as e:
            st.error(f"Error generating insights: {str(e)}")
            return ["Error generating predictive insights"]

