#!/usr/bin/env python3
"""
Sample Data Generator for Customer Analytics Dashboard
Generates realistic e-commerce transaction data for testing and demonstration
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_sample_data(num_records=5000, start_date='2023-01-01', end_date='2024-08-01'):
    """
    Generate realistic e-commerce customer transaction data
    
    Args:
        num_records: Number of transaction records to generate
        start_date: Start date for transactions
        end_date: End date for transactions
    
    Returns:
        pd.DataFrame: Generated sample data
    """
    np.random.seed(42)
    random.seed(42)
    
    # Customer segments with different behaviors
    customer_segments = {
        'high_value': {'count': 50, 'freq_mult': 3.0, 'amount_mult': 2.5},
        'medium_value': {'count': 200, 'freq_mult': 1.5, 'amount_mult': 1.2},
        'low_value': {'count': 300, 'freq_mult': 0.8, 'amount_mult': 0.7}
    }
    
    # Generate customer IDs with segments
    customers = []
    for segment, props in customer_segments.items():
        for i in range(props['count']):
            customers.append({
                'customer_id': f'C{len(customers)+1:04d}',
                'segment': segment,
                'freq_mult': props['freq_mult'],
                'amount_mult': props['amount_mult']
            })
    
    # Product catalog with categories and price ranges
    products = [
        # Electronics
        {'name': 'Wireless Headphones', 'category': 'Electronics', 'base_price': 89.99},
        {'name': 'Bluetooth Speaker', 'category': 'Electronics', 'base_price': 45.99},
        {'name': 'Smartphone Case', 'category': 'Electronics', 'base_price': 19.99},
        {'name': 'USB-C Cable', 'category': 'Electronics', 'base_price': 12.99},
        {'name': 'Wireless Charger', 'category': 'Electronics', 'base_price': 29.99},
        {'name': 'Power Bank', 'category': 'Electronics', 'base_price': 34.99},
        {'name': 'Screen Protector', 'category': 'Electronics', 'base_price': 9.99},
        {'name': 'Car Phone Mount', 'category': 'Electronics', 'base_price': 24.99},
        
        # Home & Garden
        {'name': 'Coffee Maker', 'category': 'Home', 'base_price': 79.99},
        {'name': 'Vacuum Cleaner', 'category': 'Home', 'base_price': 149.99},
        {'name': 'Air Purifier', 'category': 'Home', 'base_price': 199.99},
        {'name': 'Kitchen Scale', 'category': 'Home', 'base_price': 25.99},
        {'name': 'Storage Bins', 'category': 'Home', 'base_price': 15.99},
        {'name': 'LED Desk Lamp', 'category': 'Home', 'base_price': 39.99},
        
        # Fashion
        {'name': 'Running Shoes', 'category': 'Fashion', 'base_price': 89.99},
        {'name': 'Casual T-Shirt', 'category': 'Fashion', 'base_price': 19.99},
        {'name': 'Denim Jeans', 'category': 'Fashion', 'base_price': 59.99},
        {'name': 'Baseball Cap', 'category': 'Fashion', 'base_price': 24.99},
        {'name': 'Sunglasses', 'category': 'Fashion', 'base_price': 49.99},
        
        # Books & Media
        {'name': 'Business Strategy Book', 'category': 'Books', 'base_price': 24.99},
        {'name': 'Cookbook', 'category': 'Books', 'base_price': 29.99},
        {'name': 'Fiction Novel', 'category': 'Books', 'base_price': 14.99},
        {'name': 'Self-Help Guide', 'category': 'Books', 'base_price': 19.99}
    ]
    
    # Date range
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    date_range = (end - start).days
    
    # Generate transactions
    transactions = []
    
    for _ in range(num_records):
        # Select customer with behavior patterns
        customer = random.choice(customers)
        
        # Generate order date with seasonal patterns
        days_from_start = np.random.randint(0, date_range)
        order_date = start + timedelta(days=days_from_start)
        
        # Add seasonal boost (holiday seasons)
        month = order_date.month
        seasonal_mult = 1.0
        if month in [11, 12]:  # Holiday season
            seasonal_mult = 1.4
        elif month in [6, 7, 8]:  # Summer season
            seasonal_mult = 1.1
        
        # Select product
        product = random.choice(products)
        
        # Generate quantity (most orders are 1-2 items)
        quantity = np.random.choice([1, 2, 3, 4], p=[0.6, 0.25, 0.1, 0.05])
        
        # Calculate price with variations and customer segment impact
        price_variation = np.random.uniform(0.9, 1.1)  # ±10% price variation
        unit_price = round(
            product['base_price'] * 
            price_variation * 
            customer['amount_mult'] * 
            seasonal_mult, 
            2
        )
        
        total_amount = round(quantity * unit_price, 2)
        
        transaction = {
            'customer_id': customer['customer_id'],
            'order_date': order_date.strftime('%Y-%m-%d'),
            'product_name': product['name'],
            'product_category': product['category'],
            'quantity': quantity,
            'unit_price': unit_price,
            'total_amount': total_amount
        }
        
        transactions.append(transaction)
    
    # Create DataFrame and sort by date and customer
    df = pd.DataFrame(transactions)
    df = df.sort_values(['order_date', 'customer_id']).reset_index(drop=True)
    
    return df

def add_customer_behavior_patterns(df):
    """
    Add realistic customer behavior patterns to the data
    """
    # Calculate customer statistics for behavioral adjustments
    customer_stats = df.groupby('customer_id').agg({
        'order_date': ['min', 'count'],
        'total_amount': 'mean'
    })
    
    customer_stats.columns = ['first_order', 'order_count', 'avg_amount']
    customer_stats.reset_index(inplace=True)
    
    # Identify high-value customers for repeat purchase patterns
    high_value_customers = customer_stats[
        (customer_stats['order_count'] >= 3) & 
        (customer_stats['avg_amount'] >= 50)
    ]['customer_id'].tolist()
    
    # Add additional orders for high-value customers
    additional_orders = []
    for customer_id in high_value_customers[:20]:  # Top 20 high-value customers
        customer_orders = df[df['customer_id'] == customer_id]
        last_order = customer_orders['order_date'].max()
        
        # Add 1-3 more recent orders
        for i in range(np.random.randint(1, 4)):
            days_forward = np.random.randint(7, 60)
            new_date = pd.to_datetime(last_order) + timedelta(days=days_forward)
            
            if new_date <= pd.to_datetime('2024-08-01'):
                # Copy a random existing order for this customer but with new date
                base_order = customer_orders.sample(1).iloc[0]
                new_order = base_order.copy()
                new_order['order_date'] = new_date.strftime('%Y-%m-%d')
                
                additional_orders.append(new_order.to_dict())
    
    if additional_orders:
        additional_df = pd.DataFrame(additional_orders)
        df = pd.concat([df, additional_df], ignore_index=True)
        df = df.sort_values(['order_date', 'customer_id']).reset_index(drop=True)
    
    return df

def main():
    """Generate and save sample data files"""
    print("📊 Generating Customer Analytics Sample Data")
    print("=" * 50)
    
    # Generate different sized datasets
    datasets = [
        {'name': 'small_sample', 'records': 1000, 'description': 'Small dataset (1K records)'},
        {'name': 'medium_sample', 'records': 5000, 'description': 'Medium dataset (5K records)'},
        {'name': 'large_sample', 'records': 15000, 'description': 'Large dataset (15K records)'}
    ]
    
    for dataset in datasets:
        print(f"\n🔄 Generating {dataset['description']}...")
        
        # Generate base data
        df = generate_sample_data(
            num_records=dataset['records'],
            start_date='2023-01-01',
            end_date='2024-08-01'
        )
        
        # Add behavioral patterns
        df = add_customer_behavior_patterns(df)
        
        # Remove product_category for the main file (keep it simple)
        df_main = df.drop('product_category', axis=1)
        
        # Save main sample file
        filename = f"sample_data/{dataset['name']}.csv"
        df_main.to_csv(filename, index=False)
        
        # Generate summary
        summary = {
            'Total Records': len(df_main),
            'Unique Customers': df_main['customer_id'].nunique(),
            'Unique Products': df_main['product_name'].nunique(),
            'Date Range': f"{df_main['order_date'].min()} to {df_main['order_date'].max()}",
            'Total Revenue': f"${df_main['total_amount'].sum():,.2f}",
            'Avg Order Value': f"${df_main['total_amount'].mean():.2f}"
        }
        
        print(f"✅ Generated {filename}")
        for key, value in summary.items():
            print(f"   {key}: {value}")
    
    # Generate a comprehensive sample with categories
    print(f"\n🔄 Generating comprehensive sample with product categories...")
    df_comprehensive = generate_sample_data(num_records=8000)
    df_comprehensive = add_customer_behavior_patterns(df_comprehensive)
    df_comprehensive.to_csv("sample_data/comprehensive_sample.csv", index=False)
    print("✅ Generated sample_data/comprehensive_sample.csv")
    
    print(f"\n🎉 Sample data generation complete!")
    print(f"   Files created in 'sample_data/' directory")
    print(f"   Use these files to test the Customer Analytics Dashboard")

if __name__ == "__main__":
    main()