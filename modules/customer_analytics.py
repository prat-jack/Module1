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
    
    def cohort_analysis(self) -> Dict[str, Any]:
        """
        Perform comprehensive cohort analysis with detailed retention insights.
        
        Returns:
            dict: Complete cohort analysis with retention rates, revenue, and insights
        """
        try:
            df = self.df.copy()
            df['order_period'] = df['order_date'].dt.to_period('M')
            
            # Create cohort groups based on first purchase month
            cohort = df.groupby('customer_id')['order_date'].min().reset_index()
            cohort.columns = ['customer_id', 'cohort_group']
            cohort['cohort_group'] = cohort['cohort_group'].dt.to_period('M')
            
            df = df.merge(cohort, on='customer_id')
            df['period_number'] = (df['order_period'] - df['cohort_group']).apply(lambda x: x.n)
            
            # Basic retention cohort table
            cohort_data = df.groupby(['cohort_group', 'period_number'])['customer_id'].nunique().reset_index()
            cohort_sizes = df.groupby('cohort_group')['customer_id'].nunique().reset_index()
            cohort_table = cohort_data.merge(cohort_sizes, on='cohort_group')
            cohort_table['retention_rate'] = cohort_table['customer_id_x'] / cohort_table['customer_id_y']
            
            retention_table = cohort_table.pivot(index='cohort_group', 
                                                columns='period_number', 
                                                values='retention_rate').fillna(0)
            
            # Revenue cohort analysis
            revenue_data = df.groupby(['cohort_group', 'period_number'])['total_amount'].sum().reset_index()
            cohort_revenue = cohort_data.merge(cohort_sizes, on='cohort_group')
            cohort_revenue = cohort_revenue.merge(revenue_data, on=['cohort_group', 'period_number'])
            cohort_revenue['revenue_per_customer'] = cohort_revenue['total_amount'] / cohort_revenue['customer_id_y']
            
            revenue_table = cohort_revenue.pivot(index='cohort_group',
                                               columns='period_number',
                                               values='revenue_per_customer').fillna(0)
            
            # Customer count cohort table (absolute numbers)
            count_table = cohort_table.pivot(index='cohort_group',
                                            columns='period_number', 
                                            values='customer_id_x').fillna(0)
            
            # Calculate retention insights
            retention_insights = self._calculate_retention_insights(retention_table, revenue_table, count_table)
            
            # Calculate cohort performance metrics
            cohort_performance = self._calculate_cohort_performance(df, cohort_sizes)
            
            # Predict future retention
            retention_predictions = self._predict_retention_trends(retention_table)
            
            # Convert DataFrames to ensure JSON compatibility
            retention_table_clean = retention_table.round(3)
            retention_table_clean.index = retention_table_clean.index.astype(str)
            
            revenue_table_clean = revenue_table.round(2) 
            revenue_table_clean.index = revenue_table_clean.index.astype(str)
            
            count_table_clean = count_table.astype(int)
            count_table_clean.index = count_table_clean.index.astype(str)
            
            return {
                'retention_table': retention_table_clean,
                'revenue_table': revenue_table_clean,
                'count_table': count_table_clean,
                'cohort_sizes': dict(zip(cohort_sizes['cohort_group'].astype(str), cohort_sizes['customer_id'])),
                'retention_insights': retention_insights,
                'cohort_performance': cohort_performance,
                'retention_predictions': retention_predictions,
                'analysis_summary': {
                    'total_cohorts': len(cohort_sizes),
                    'avg_cohort_size': int(cohort_sizes['customer_id'].mean()),
                    'oldest_cohort': str(cohort_sizes['cohort_group'].min()),
                    'newest_cohort': str(cohort_sizes['cohort_group'].max())
                }
            }
            
        except Exception as e:
            st.error(f"Error in cohort analysis: {str(e)}")
            return {}
    
    def _calculate_retention_insights(self, retention_table: pd.DataFrame, revenue_table: pd.DataFrame, count_table: pd.DataFrame) -> Dict[str, Any]:
        """Calculate detailed retention insights from cohort data."""
        try:
            insights = {}
            
            if not retention_table.empty and retention_table.shape[1] > 1:
                # Overall retention rates by period
                avg_retention_by_period = retention_table.mean()
                insights['avg_retention_by_period'] = avg_retention_by_period.round(3).to_dict()
                
                # Best and worst performing cohorts
                if retention_table.shape[1] >= 3:  # At least 3 periods
                    period_3_retention = retention_table.iloc[:, min(3, retention_table.shape[1]-1)]
                    best_cohort = period_3_retention.idxmax()
                    worst_cohort = period_3_retention.idxmin()
                    
                    insights['best_cohort'] = {
                        'period': str(best_cohort),
                        'retention_rate': period_3_retention[best_cohort]
                    }
                    insights['worst_cohort'] = {
                        'period': str(worst_cohort),
                        'retention_rate': period_3_retention[worst_cohort]
                    }
                
                # Retention drop-off analysis
                if retention_table.shape[1] > 1:
                    month_1_retention = retention_table.iloc[:, 1].mean() if retention_table.shape[1] > 1 else 0
                    month_3_retention = retention_table.iloc[:, 3].mean() if retention_table.shape[1] > 3 else 0
                    month_6_retention = retention_table.iloc[:, 6].mean() if retention_table.shape[1] > 6 else 0
                    
                    insights['retention_milestones'] = {
                        '1_month': round(month_1_retention, 3),
                        '3_months': round(month_3_retention, 3),
                        '6_months': round(month_6_retention, 3)
                    }
                
                # Revenue retention correlation
                if not revenue_table.empty:
                    # Calculate correlation between retention and revenue per customer
                    correlation_data = []
                    for col in retention_table.columns:
                        if col in revenue_table.columns:
                            ret_values = retention_table[col].values
                            rev_values = revenue_table[col].values
                            # Filter out zeros for meaningful correlation
                            valid_indices = (ret_values > 0) & (rev_values > 0)
                            if np.sum(valid_indices) > 2:
                                correlation = np.corrcoef(ret_values[valid_indices], rev_values[valid_indices])[0, 1]
                                correlation_data.append(correlation)
                    
                    if correlation_data:
                        insights['retention_revenue_correlation'] = round(np.mean(correlation_data), 3)
            
            return insights
            
        except Exception as e:
            return {}
    
    def _calculate_cohort_performance(self, df: pd.DataFrame, cohort_sizes: pd.DataFrame) -> Dict[str, Any]:
        """Calculate performance metrics for each cohort."""
        try:
            cohort_performance = {}
            
            for _, row in cohort_sizes.iterrows():
                cohort_period = row['cohort_group']
                cohort_customers = df[df['cohort_group'] == cohort_period]
                
                if len(cohort_customers) > 0:
                    performance = {
                        'total_customers': int(row['customer_id']),
                        'total_revenue': cohort_customers['total_amount'].sum(),
                        'avg_customer_value': cohort_customers.groupby('customer_id')['total_amount'].sum().mean(),
                        'avg_orders_per_customer': len(cohort_customers) / row['customer_id'],
                        'avg_order_value': cohort_customers['total_amount'].mean(),
                        'active_months': cohort_customers['period_number'].max() + 1,
                        'purchase_frequency': len(cohort_customers) / ((cohort_customers['period_number'].max() + 1) * row['customer_id'])
                    }
                    
                    cohort_performance[str(cohort_period)] = {k: round(v, 2) if isinstance(v, float) else v 
                                                            for k, v in performance.items()}
            
            return cohort_performance
            
        except Exception as e:
            return {}
    
    def _predict_retention_trends(self, retention_table: pd.DataFrame) -> Dict[str, Any]:
        """Predict future retention trends based on historical data."""
        try:
            predictions = {}
            
            if not retention_table.empty and retention_table.shape[1] > 2:
                # Calculate average retention decay rate
                avg_retention_by_period = retention_table.mean()
                
                if len(avg_retention_by_period) > 2:
                    # Calculate decay rate between periods
                    decay_rates = []
                    for i in range(1, min(6, len(avg_retention_by_period))):
                        if avg_retention_by_period.iloc[i-1] > 0:
                            decay_rate = 1 - (avg_retention_by_period.iloc[i] / avg_retention_by_period.iloc[i-1])
                            decay_rates.append(decay_rate)
                    
                    if decay_rates:
                        avg_decay_rate = np.mean(decay_rates)
                        
                        # Predict next 3 months retention
                        last_retention = avg_retention_by_period.iloc[-1]
                        predicted_retention = []
                        current_retention = last_retention
                        
                        for month in range(1, 4):
                            current_retention = current_retention * (1 - avg_decay_rate)
                            predicted_retention.append(max(0, current_retention))
                        
                        predictions['predicted_retention_next_3_months'] = [round(x, 3) for x in predicted_retention]
                        predictions['avg_monthly_decay_rate'] = round(avg_decay_rate, 3)
                        
                        # Estimate long-term retention
                        if avg_decay_rate < 0.5:  # Reasonable decay rate
                            steady_state = last_retention * (1 - avg_decay_rate) ** 12
                            predictions['estimated_12_month_retention'] = round(max(0, steady_state), 3)
            
            return predictions
            
        except Exception as e:
            return {}
    
    def identify_churn_risk(self) -> pd.DataFrame:
        """
        Identify customers at risk of churning with advanced behavioral indicators.
        
        Returns:
            pd.DataFrame: Customers with comprehensive churn risk analysis
        """
        try:
            if self.rfm_data is None:
                self.calculate_rfm()
            
            if self.rfm_data.empty:
                return pd.DataFrame()
            
            churn_data = self.rfm_data.copy()
            
            # Enhanced churn indicators
            customer_behavior = self.df.groupby('customer_id').agg({
                'order_date': ['count', 'min', 'max'],
                'total_amount': ['mean', 'std', 'sum'],
                'product_name': 'nunique'
            }).round(2)
            
            customer_behavior.columns = [
                'total_orders', 'first_purchase', 'last_purchase', 
                'avg_order_value', 'order_value_std', 'total_spent', 'unique_products'
            ]
            customer_behavior.reset_index(inplace=True)
            
            # Calculate advanced churn indicators
            customer_behavior['days_since_first'] = (self.reference_date - customer_behavior['first_purchase']).dt.days
            customer_behavior['purchase_consistency'] = customer_behavior['order_value_std'] / customer_behavior['avg_order_value']
            customer_behavior['purchase_diversity'] = customer_behavior['unique_products'] / customer_behavior['total_orders']
            customer_behavior['order_frequency'] = customer_behavior['total_orders'] / customer_behavior['days_since_first'] * 30
            
            # Merge with RFM data
            churn_data = churn_data.merge(customer_behavior, on='customer_id', how='left')
            
            # Calculate advanced churn score with multiple indicators
            churn_data['churn_score'] = (
                churn_data['recency'] * 0.25 +  # Days since last purchase
                (6 - churn_data['frequency']) * 8 * 0.20 +  # Purchase frequency
                (6 - churn_data['M_score']) * 8 * 0.20 +  # Monetary value
                (1 / (churn_data['order_frequency'] + 0.1)) * 100 * 0.15 +  # Order frequency trend
                churn_data['purchase_consistency'].fillna(1) * 20 * 0.10 +  # Consistency
                (1 - churn_data['purchase_diversity'].fillna(0.5)) * 50 * 0.10  # Product diversity
            )
            
            # Normalize churn score to 0-100 range
            churn_data['churn_score'] = ((churn_data['churn_score'] - churn_data['churn_score'].min()) / 
                                       (churn_data['churn_score'].max() - churn_data['churn_score'].min()) * 100)
            
            # Enhanced risk categorization
            churn_data['risk_level'] = pd.cut(
                churn_data['churn_score'],
                bins=[0, 25, 50, 75, 100],
                labels=['Low', 'Medium', 'High', 'Critical'],
                include_lowest=True
            )
            
            # Add churn probability and recommended actions
            churn_data['churn_probability'] = (churn_data['churn_score'] / 100 * 0.8 + 0.1).round(3)
            
            def get_retention_strategy(row):
                if row['risk_level'] == 'Critical':
                    return 'Immediate intervention: Personal outreach + special offers'
                elif row['risk_level'] == 'High':
                    return 'Urgent: Targeted discounts + engagement campaigns'
                elif row['risk_level'] == 'Medium':
                    return 'Monitor closely + personalized recommendations'
                else:
                    return 'Maintain: Regular marketing + loyalty programs'
            
            churn_data['retention_strategy'] = churn_data.apply(get_retention_strategy, axis=1)
            
            # Sort by churn score descending
            churn_data = churn_data.sort_values('churn_score', ascending=False)
            
            return churn_data[[
                'customer_id', 'recency', 'frequency', 'monetary', 'segment',
                'churn_score', 'churn_probability', 'risk_level', 'retention_strategy',
                'order_frequency', 'purchase_consistency', 'purchase_diversity'
            ]]
            
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
    
    def market_basket_analysis(self, min_support: float = 0.01, min_confidence: float = 0.5) -> Dict[str, Any]:
        """
        Perform market basket analysis for product recommendations.
        
        Args:
            min_support: Minimum support threshold for frequent itemsets
            min_confidence: Minimum confidence threshold for association rules
            
        Returns:
            dict: Market basket analysis results with recommendations
        """
        try:
            # Create transaction matrix
            basket = self.df.groupby(['customer_id', 'order_date'])['product_name'].apply(list).reset_index()
            all_products = self.df['product_name'].unique()
            
            # Calculate product co-occurrence matrix
            product_combinations = {}
            product_counts = {}
            total_transactions = len(basket)
            
            # Count individual product occurrences
            for _, transaction in basket.iterrows():
                products = transaction['product_name']
                for product in products:
                    product_counts[product] = product_counts.get(product, 0) + 1
            
            # Count product pairs
            for _, transaction in basket.iterrows():
                products = transaction['product_name']
                for i, product1 in enumerate(products):
                    for j, product2 in enumerate(products):
                        if i != j:
                            pair = tuple(sorted([product1, product2]))
                            product_combinations[pair] = product_combinations.get(pair, 0) + 1
            
            # Calculate support, confidence, and lift
            recommendations = []
            for (product1, product2), co_occurrence in product_combinations.items():
                support = co_occurrence / total_transactions
                
                if support >= min_support:
                    confidence_1_to_2 = co_occurrence / product_counts[product1]
                    confidence_2_to_1 = co_occurrence / product_counts[product2]
                    
                    if confidence_1_to_2 >= min_confidence:
                        lift = confidence_1_to_2 / (product_counts[product2] / total_transactions)
                        recommendations.append({
                            'antecedent': product1,
                            'consequent': product2,
                            'support': round(support, 4),
                            'confidence': round(confidence_1_to_2, 4),
                            'lift': round(lift, 2),
                            'conviction': round(1 / (1 - confidence_1_to_2 + 0.001), 2)
                        })
                    
                    if confidence_2_to_1 >= min_confidence:
                        lift = confidence_2_to_1 / (product_counts[product1] / total_transactions)
                        recommendations.append({
                            'antecedent': product2,
                            'consequent': product1,
                            'support': round(support, 4),
                            'confidence': round(confidence_2_to_1, 4),
                            'lift': round(lift, 2),
                            'conviction': round(1 / (1 - confidence_2_to_1 + 0.001), 2)
                        })
            
            # Sort by lift and confidence
            recommendations = sorted(recommendations, key=lambda x: (x['lift'], x['confidence']), reverse=True)
            
            # Create product affinity matrix
            affinity_matrix = pd.DataFrame(index=all_products, columns=all_products, dtype=float)
            for product1 in all_products:
                for product2 in all_products:
                    if product1 != product2:
                        pair_count = product_combinations.get(tuple(sorted([product1, product2])), 0)
                        if product_counts.get(product1, 0) > 0:
                            affinity = pair_count / product_counts[product1]
                            affinity_matrix.loc[product1, product2] = affinity
                    else:
                        affinity_matrix.loc[product1, product2] = 1.0
            
            affinity_matrix = affinity_matrix.fillna(0)
            
            # Generate customer-specific recommendations
            def get_customer_recommendations(customer_id: str, top_n: int = 5) -> List[str]:
                customer_products = self.df[self.df['customer_id'] == customer_id]['product_name'].unique()
                recommendations_map = {}
                
                for product in customer_products:
                    for rec in recommendations:
                        if rec['antecedent'] == product and rec['consequent'] not in customer_products:
                            score = rec['confidence'] * rec['lift']
                            if rec['consequent'] not in recommendations_map:
                                recommendations_map[rec['consequent']] = 0
                            recommendations_map[rec['consequent']] += score
                
                sorted_recs = sorted(recommendations_map.items(), key=lambda x: x[1], reverse=True)
                return [product for product, _ in sorted_recs[:top_n]]
            
            return {
                'association_rules': recommendations[:20],  # Top 20 rules
                'affinity_matrix': affinity_matrix,
                'product_popularity': dict(sorted(product_counts.items(), key=lambda x: x[1], reverse=True)),
                'recommendation_engine': get_customer_recommendations,
                'total_transactions': total_transactions,
                'unique_products': len(all_products)
            }
            
        except Exception as e:
            st.error(f"Error in market basket analysis: {str(e)}")
            return {}
    
    def customer_journey_mapping(self) -> Dict[str, Any]:
        """
        Create comprehensive customer journey maps and touchpoint analysis.
        
        Returns:
            dict: Customer journey analysis with stages, paths, and insights
        """
        try:
            journey_data = self.df.copy()
            journey_data = journey_data.sort_values(['customer_id', 'order_date'])
            
            # Define customer lifecycle stages
            def get_customer_stage(customer_data):
                days_since_first = (self.reference_date - customer_data['order_date'].min()).days
                order_count = len(customer_data)
                total_spent = customer_data['total_amount'].sum()
                
                if days_since_first <= 30:
                    return 'New'
                elif days_since_first <= 90 and order_count >= 2:
                    return 'Developing'
                elif order_count >= 5 and total_spent > customer_data['total_amount'].mean() * 2:
                    return 'Loyal'
                elif (self.reference_date - customer_data['order_date'].max()).days > 90:
                    return 'Inactive'
                else:
                    return 'Regular'
            
            # Analyze customer journeys
            customer_journeys = {}
            stage_transitions = {}
            touchpoint_sequences = {}
            
            for customer_id in journey_data['customer_id'].unique():
                customer_orders = journey_data[journey_data['customer_id'] == customer_id].copy()
                
                # Calculate journey metrics
                journey_length = (customer_orders['order_date'].max() - customer_orders['order_date'].min()).days
                order_frequency = len(customer_orders) / max(journey_length, 1) * 30  # Orders per month
                
                # Product journey
                product_sequence = customer_orders['product_name'].tolist()
                unique_products = customer_orders['product_name'].nunique()
                
                # Value journey
                spending_trend = customer_orders['total_amount'].tolist()
                avg_order_value = customer_orders['total_amount'].mean()
                value_volatility = customer_orders['total_amount'].std() / avg_order_value if avg_order_value > 0 else 0
                
                current_stage = get_customer_stage(customer_orders)
                
                customer_journeys[customer_id] = {
                    'current_stage': current_stage,
                    'journey_length_days': journey_length,
                    'total_touchpoints': len(customer_orders),
                    'order_frequency': round(order_frequency, 2),
                    'unique_products': unique_products,
                    'product_diversity': round(unique_products / len(customer_orders), 2),
                    'avg_order_value': round(avg_order_value, 2),
                    'value_volatility': round(value_volatility, 2),
                    'total_clv': round(customer_orders['total_amount'].sum(), 2),
                    'first_purchase': customer_orders['order_date'].min(),
                    'last_purchase': customer_orders['order_date'].max(),
                    'product_sequence': product_sequence[:10],  # First 10 products
                    'spending_progression': spending_trend[:10]  # First 10 orders
                }
            
            # Analyze stage distribution
            stage_distribution = {}
            for journey in customer_journeys.values():
                stage = journey['current_stage']
                stage_distribution[stage] = stage_distribution.get(stage, 0) + 1
            
            # Calculate average metrics by stage
            stage_metrics = {}
            for stage in stage_distribution.keys():
                stage_customers = [j for j in customer_journeys.values() if j['current_stage'] == stage]
                if stage_customers:
                    stage_metrics[stage] = {
                        'count': len(stage_customers),
                        'avg_journey_length': np.mean([c['journey_length_days'] for c in stage_customers]),
                        'avg_touchpoints': np.mean([c['total_touchpoints'] for c in stage_customers]),
                        'avg_clv': np.mean([c['total_clv'] for c in stage_customers]),
                        'avg_order_frequency': np.mean([c['order_frequency'] for c in stage_customers]),
                        'avg_product_diversity': np.mean([c['product_diversity'] for c in stage_customers])
                    }
            
            # Identify common journey patterns
            journey_patterns = self._identify_journey_patterns(customer_journeys)
            
            # Calculate conversion metrics
            conversion_metrics = self._calculate_conversion_metrics(journey_data)
            
            # Generate journey insights
            insights = self._generate_journey_insights(stage_metrics, journey_patterns)
            
            return {
                'customer_journeys': customer_journeys,
                'stage_distribution': stage_distribution,
                'stage_metrics': stage_metrics,
                'journey_patterns': journey_patterns,
                'conversion_metrics': conversion_metrics,
                'insights': insights,
                'total_customers_analyzed': len(customer_journeys)
            }
            
        except Exception as e:
            st.error(f"Error in customer journey mapping: {str(e)}")
            return {}
    
    def _identify_journey_patterns(self, customer_journeys: Dict) -> Dict[str, Any]:
        """Identify common customer journey patterns."""
        try:
            patterns = {
                'quick_converters': [],  # New to Loyal quickly
                'gradual_builders': [],  # Slow progression
                'high_value_starters': [],  # High initial orders
                'product_explorers': [],  # High product diversity
                'consistent_buyers': [],  # Regular purchase intervals
                'at_risk_patterns': []  # Declining engagement
            }
            
            for customer_id, journey in customer_journeys.items():
                # Quick converters: Loyal within 60 days
                if journey['current_stage'] == 'Loyal' and journey['journey_length_days'] <= 60:
                    patterns['quick_converters'].append(customer_id)
                
                # Gradual builders: Long journey, multiple stages
                elif journey['journey_length_days'] > 180 and journey['total_touchpoints'] >= 5:
                    patterns['gradual_builders'].append(customer_id)
                
                # High value starters: First order > average
                elif len(journey['spending_progression']) > 0 and journey['spending_progression'][0] > journey['avg_order_value'] * 1.5:
                    patterns['high_value_starters'].append(customer_id)
                
                # Product explorers: High diversity
                elif journey['product_diversity'] > 0.7:
                    patterns['product_explorers'].append(customer_id)
                
                # Consistent buyers: Low value volatility, regular frequency
                elif journey['value_volatility'] < 0.5 and journey['order_frequency'] > 1:
                    patterns['consistent_buyers'].append(customer_id)
                
                # At risk: Inactive or declining
                elif journey['current_stage'] == 'Inactive':
                    patterns['at_risk_patterns'].append(customer_id)
            
            return {k: len(v) for k, v in patterns.items()}
            
        except Exception as e:
            return {}
    
    def _calculate_conversion_metrics(self, journey_data: pd.DataFrame) -> Dict[str, float]:
        """Calculate key conversion metrics across the customer journey."""
        try:
            total_customers = journey_data['customer_id'].nunique()
            
            # Calculate stage conversions
            stage_counts = {}
            for customer_id in journey_data['customer_id'].unique():
                customer_orders = journey_data[journey_data['customer_id'] == customer_id]
                days_active = (customer_orders['order_date'].max() - customer_orders['order_date'].min()).days
                order_count = len(customer_orders)
                
                if days_active <= 30:
                    stage = 'new'
                elif order_count >= 2:
                    stage = 'repeat'
                    if order_count >= 5:
                        stage = 'loyal'
                else:
                    stage = 'one_time'
                
                stage_counts[stage] = stage_counts.get(stage, 0) + 1
            
            return {
                'new_to_repeat_rate': round((stage_counts.get('repeat', 0) + stage_counts.get('loyal', 0)) / total_customers * 100, 2),
                'repeat_to_loyal_rate': round(stage_counts.get('loyal', 0) / max(stage_counts.get('repeat', 1), 1) * 100, 2),
                'one_time_customer_rate': round(stage_counts.get('one_time', 0) / total_customers * 100, 2),
                'customer_lifecycle_ratio': round(stage_counts.get('loyal', 0) / stage_counts.get('new', 1), 2)
            }
            
        except Exception as e:
            return {}
    
    def _generate_journey_insights(self, stage_metrics: Dict, journey_patterns: Dict) -> List[str]:
        """Generate actionable insights from journey analysis."""
        insights = []
        
        try:
            total_customers = sum(stage_metrics[stage]['count'] for stage in stage_metrics)
            
            # Stage distribution insights
            for stage, metrics in stage_metrics.items():
                percentage = (metrics['count'] / total_customers) * 100
                if percentage > 40:
                    insights.append(f"{stage} customers represent {percentage:.1f}% of your base - consider stage-specific strategies")
            
            # Journey pattern insights
            if journey_patterns.get('quick_converters', 0) > 0:
                insights.append(f"{journey_patterns['quick_converters']} customers converted quickly - identify and replicate success factors")
            
            if journey_patterns.get('at_risk_patterns', 0) > 0:
                insights.append(f"{journey_patterns['at_risk_patterns']} customers show at-risk patterns - implement retention campaigns")
            
            if journey_patterns.get('product_explorers', 0) > 0:
                insights.append(f"{journey_patterns['product_explorers']} customers explore many products - leverage for cross-selling")
            
            # CLV insights by stage
            if 'Loyal' in stage_metrics and 'New' in stage_metrics:
                loyal_clv = stage_metrics['Loyal']['avg_clv']
                new_clv = stage_metrics['New']['avg_clv']
                if loyal_clv > new_clv * 3:
                    insights.append(f"Loyal customers generate {loyal_clv/new_clv:.1f}x more value - focus on loyalty conversion")
            
            return insights[:6]  # Return top 6 insights
            
        except Exception as e:
            return ["Error generating journey insights"]

