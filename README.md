# Customer Analytics Dashboard

A comprehensive Python-based customer analytics dashboard application designed for e-commerce businesses to gain deep insights into customer behavior, sales performance, and business intelligence.

## Business Context

**Target Users**: Sales managers, marketing teams, executives  
**Primary Goal**: Identify high-value customers and growth opportunities  
**Data Focus**: E-commerce transaction analysis and customer intelligence

## Key Features

### Customer Segmentation
- **RFM Analysis** (Recency, Frequency, Monetary)
- **Customer Lifetime Value** (CLV) calculation
- **Advanced ML-based segmentation**
- **Churn risk identification**
- **Cohort analysis**

### Sales Performance Analytics
- **Revenue trends and growth metrics**
- **Product performance analysis**
- **Seasonal sales patterns**
- **Customer acquisition trends**
- **Pricing impact analysis**

### Interactive Business Intelligence Dashboard
- **Real-time KPI monitoring**
- **Interactive Plotly visualizations**
- **Advanced filtering and date range selection**
- **Professional business theme**
- **Export capabilities**

## Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

2. **Activate the virtual environment:**
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Generate sample data (optional):**
   ```bash
   python generate_sample_data.py
   ```

5. **Run the dashboard:**
   ```bash
   python run.py
   ```
   
   Or directly with Streamlit:
   ```bash
   streamlit run app.py
   ```

6. **Open your browser:**
   - The dashboard will automatically open at `http://localhost:8501`

## Data Requirements

### CSV Format
Your CSV file must contain the following columns:

| Column | Type | Description |
|--------|------|-------------|
| `customer_id` | String | Unique customer identifier |
| `order_date` | Date | Order date (YYYY-MM-DD format) |
| `product_name` | String | Name of purchased product |
| `quantity` | Integer | Number of items purchased |
| `unit_price` | Float | Price per unit |
| `total_amount` | Float | Total order amount |

### Sample Data
```csv
customer_id,order_date,product_name,quantity,unit_price,total_amount
C0001,2024-01-15,Wireless Headphones,1,89.99,89.99
C0002,2024-01-16,Coffee Maker,2,79.99,159.98
C0001,2024-02-01,Bluetooth Speaker,1,45.99,45.99
```

## Analytics Features

### Customer Segmentation
- **Champions**: Best customers (high RFM scores)
- **Loyal Customers**: Regular buyers with good value
- **Potential Loyalists**: Good recent customers
- **At Risk**: Valuable customers who haven't purchased recently
- **Lost Customers**: Previous customers who've stopped buying

### Key Metrics
- Customer Lifetime Value (CLV)
- Customer Acquisition Cost trends
- Repeat purchase rate
- Average Order Value (AOV)
- Revenue growth rate
- Customer churn risk scores

## Technical Details

### Dependencies
- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive visualizations
- **Scikit-learn**: Machine learning for advanced segmentation
- **NumPy**: Numerical computing

### Performance Optimization
- Efficient data processing with pandas
- Streamlit caching for repeated operations
- Chunked processing for large datasets
- Optimized visualization rendering

## Project Structure

```
customer-analytics-dashboard/
├── app.py                      # Main Streamlit application
├── config.py                   # Configuration settings
├── run.py                      # Application runner script
├── generate_sample_data.py     # Sample data generator
├── requirements.txt            # Python dependencies
├── modules/
│   ├── __init__.py
│   ├── data_processor.py       # Data loading and validation
│   ├── customer_analytics.py   # Customer segmentation logic
│   └── sales_analytics.py      # Sales performance metrics
├── sample_data/               # Generated sample datasets
├── .streamlit/
│   └── config.toml            # Streamlit configuration
└── README.md                  # This file
```

## Usage

1. **Customer Segmentation Analysis**
   - Upload your transaction data
   - Navigate to "Customer Segmentation"
   - Review RFM analysis and customer segments
   - Identify high-value customers for retention campaigns

2. **Sales Performance Review**
   - Select "Sales Performance" from the sidebar
   - Analyze monthly revenue trends
   - Identify top-performing products
   - Review growth metrics and KPIs

3. **Advanced Analytics**
   - Go to "Advanced Analytics"
   - Explore cohort analysis for retention insights
   - Review predictive insights and recommendations
   - Identify customers at risk of churning

Ready to gain insights into your customer data? Start by running `python run.py` and uploading your CSV data to explore powerful customer analytics!