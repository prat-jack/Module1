import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st
from typing import Optional, Dict, List, Any
import io

class DataProcessor:
    """
    Data processing module for customer analytics dashboard.
    Handles CSV loading, validation, cleaning, and transformation.
    """
    
    def __init__(self):
        self.required_columns = [
            'customer_id', 'order_date', 'product_name', 
            'quantity', 'unit_price', 'total_amount'
        ]
        self.optional_columns = [
            'country', 'region', 'city'
        ]
        
    def load_and_validate_data(self, uploaded_file) -> Optional[pd.DataFrame]:
        """
        Load and validate CSV data with comprehensive error handling.
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            pd.DataFrame or None if validation fails
        """
        try:
            df = pd.read_csv(uploaded_file)
            
            if self._validate_columns(df):
                df = self._clean_and_transform_data(df)
                if self._validate_data_quality(df):
                    return df
            
            return None
            
        except Exception as e:
            st.error(f"Error loading CSV file: {str(e)}")
            return None
    
    def _validate_columns(self, df: pd.DataFrame) -> bool:
        """
        Validate that all required columns are present.
        
        Args:
            df: Input DataFrame
            
        Returns:
            bool: True if all required columns present
        """
        missing_columns = [col for col in self.required_columns if col not in df.columns]
        
        if missing_columns:
            st.error(f"Missing required columns: {', '.join(missing_columns)}")
            st.info(f"Required columns: {', '.join(self.required_columns)}")
            return False
        
        return True
    
    def _clean_and_transform_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and transform the raw data.
        
        Args:
            df: Input DataFrame
            
        Returns:
            pd.DataFrame: Cleaned DataFrame
        """
        df = df.copy()
        
        try:
            df['order_date'] = pd.to_datetime(df['order_date'])
        except:
            st.error("Invalid date format in 'order_date' column. Expected format: YYYY-MM-DD")
            return df
        
        df['customer_id'] = df['customer_id'].astype(str)
        df['product_name'] = df['product_name'].astype(str)
        
        # Handle optional geographic columns
        for col in self.optional_columns:
            if col in df.columns:
                df[col] = df[col].astype(str)
                df[col] = df[col].replace(['nan', 'NaN', 'None', ''], 'Unknown')
        
        numeric_columns = ['quantity', 'unit_price', 'total_amount']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        initial_rows = len(df)
        df = df.dropna()
        
        if len(df) < initial_rows:
            dropped_rows = initial_rows - len(df)
            st.warning(f"Dropped {dropped_rows} rows with missing or invalid data")
        
        df = df[df['quantity'] > 0]
        df = df[df['unit_price'] > 0]
        df = df[df['total_amount'] > 0]
        
        df['calculated_total'] = df['quantity'] * df['unit_price']
        df['total_difference'] = abs(df['total_amount'] - df['calculated_total'])
        
        inconsistent_rows = df[df['total_difference'] > 0.01]
        if len(inconsistent_rows) > 0:
            st.warning(f"Found {len(inconsistent_rows)} rows with inconsistent totals. Using calculated totals.")
            df['total_amount'] = df['calculated_total']
        
        df = df.drop(['calculated_total', 'total_difference'], axis=1)
        
        df = df.sort_values(['customer_id', 'order_date']).reset_index(drop=True)
        
        return df
    
    def _validate_data_quality(self, df: pd.DataFrame) -> bool:
        """
        Perform data quality checks.
        
        Args:
            df: Cleaned DataFrame
            
        Returns:
            bool: True if data quality is acceptable
        """
        if len(df) == 0:
            st.error("No valid data rows found after cleaning")
            return False
        
        if len(df) > 100000:
            st.warning("Dataset is large (>100K records). Performance may be impacted.")
        
        date_range = (df['order_date'].max() - df['order_date'].min()).days
        if date_range < 30:
            st.warning("Date range is less than 30 days. Some analytics may be limited.")
        
        unique_customers = df['customer_id'].nunique()
        if unique_customers < 10:
            st.warning("Few unique customers found. Segmentation analysis may be limited.")
        
        st.success(f"Data validation successful: {len(df):,} records, {unique_customers:,} customers")
        
        return True
    
    def get_data_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate comprehensive data summary statistics.
        
        Args:
            df: Input DataFrame
            
        Returns:
            dict: Summary statistics
        """
        summary = {
            'total_records': len(df),
            'unique_customers': df['customer_id'].nunique(),
            'unique_products': df['product_name'].nunique(),
            'date_range': {
                'start': df['order_date'].min(),
                'end': df['order_date'].max(),
                'days': (df['order_date'].max() - df['order_date'].min()).days
            },
            'revenue_stats': {
                'total': df['total_amount'].sum(),
                'mean': df['total_amount'].mean(),
                'median': df['total_amount'].median(),
                'std': df['total_amount'].std()
            },
            'quantity_stats': {
                'total': df['quantity'].sum(),
                'mean': df['quantity'].mean(),
                'max': df['quantity'].max()
            },
            'orders_per_customer': {
                'mean': len(df) / df['customer_id'].nunique(),
                'distribution': df.groupby('customer_id').size().describe()
            }
        }
        
        return summary
    
    def generate_sample_data(self, num_records: int = 1000) -> pd.DataFrame:
        """
        Generate sample customer transaction data for testing.
        
        Args:
            num_records: Number of records to generate
            
        Returns:
            pd.DataFrame: Sample data
        """
        np.random.seed(42)
        
        customers = [f'C{i:04d}' for i in range(1, 201)]
        products = [
            'Laptop', 'Smartphone', 'Tablet', 'Headphones', 'Keyboard', 
            'Mouse', 'Monitor', 'Webcam', 'Speaker', 'Charger',
            'Phone Case', 'Screen Protector', 'USB Cable', 'Power Bank',
            'Wireless Earbuds', 'Smart Watch', 'Fitness Tracker', 'Router'
        ]
        
        countries = ['United States', 'Canada', 'United Kingdom', 'Germany', 'France', 
                    'Australia', 'Japan', 'Brazil', 'India', 'Mexico']
        regions = {
            'United States': ['California', 'Texas', 'New York', 'Florida', 'Illinois'],
            'Canada': ['Ontario', 'Quebec', 'British Columbia', 'Alberta', 'Manitoba'],
            'United Kingdom': ['England', 'Scotland', 'Wales', 'Northern Ireland'],
            'Germany': ['Bavaria', 'North Rhine-Westphalia', 'Baden-Württemberg', 'Lower Saxony'],
            'France': ['Île-de-France', 'Auvergne-Rhône-Alpes', 'Occitanie', 'Nouvelle-Aquitaine'],
            'Australia': ['New South Wales', 'Victoria', 'Queensland', 'Western Australia'],
            'Japan': ['Tokyo', 'Osaka', 'Kanagawa', 'Aichi', 'Saitama'],
            'Brazil': ['São Paulo', 'Rio de Janeiro', 'Minas Gerais', 'Bahia'],
            'India': ['Maharashtra', 'Karnataka', 'Tamil Nadu', 'Delhi', 'Gujarat'],
            'Mexico': ['Mexico City', 'Jalisco', 'Nuevo León', 'Puebla', 'Guanajuato']
        }
        cities = {
            'California': ['Los Angeles', 'San Francisco', 'San Diego', 'San Jose'],
            'Texas': ['Houston', 'Dallas', 'Austin', 'San Antonio'],
            'New York': ['New York City', 'Buffalo', 'Rochester', 'Syracuse'],
            'Florida': ['Miami', 'Tampa', 'Orlando', 'Jacksonville'],
            'Ontario': ['Toronto', 'Ottawa', 'Hamilton', 'London'],
            'England': ['London', 'Manchester', 'Birmingham', 'Liverpool'],
            'Bavaria': ['Munich', 'Nuremberg', 'Augsburg', 'Würzburg']
        }
        
        data = []
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2024, 8, 1)
        
        for _ in range(num_records):
            customer_id = np.random.choice(customers)
            order_date = start_date + timedelta(
                days=np.random.randint(0, (end_date - start_date).days)
            )
            product_name = np.random.choice(products)
            quantity = np.random.randint(1, 5)
            unit_price = round(np.random.uniform(10, 500), 2)
            total_amount = round(quantity * unit_price, 2)
            
            # Generate geographic data
            country = np.random.choice(countries)
            region = np.random.choice(regions.get(country, ['Unknown']))
            city = np.random.choice(cities.get(region, [f'{region} City']))
            
            data.append({
                'customer_id': customer_id,
                'order_date': order_date.strftime('%Y-%m-%d'),
                'product_name': product_name,
                'quantity': quantity,
                'unit_price': unit_price,
                'total_amount': total_amount,
                'country': country,
                'region': region,
                'city': city
            })
        
        return pd.DataFrame(data)
    
    def export_data(self, df: pd.DataFrame, format_type: str = 'csv') -> bytes:
        """
        Export processed data in specified format.
        
        Args:
            df: DataFrame to export
            format_type: Export format ('csv', 'excel')
            
        Returns:
            bytes: Exported data
        """
        if format_type == 'csv':
            return df.to_csv(index=False).encode('utf-8')
        elif format_type == 'excel':
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Customer Data')
            return output.getvalue()
        else:
            raise ValueError(f"Unsupported export format: {format_type}")