# Customer Analytics Dashboard

A production-ready, enterprise-grade customer analytics dashboard designed for e-commerce businesses to gain deep insights into customer behavior, sales performance, and business intelligence. Now optimized for Streamlit Cloud deployment with comprehensive security, monitoring, and performance features.

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

### Geographic Analytics
- **Regional performance analysis**
- **Market penetration insights**
- **Geographic customer segmentation**
- **Expansion opportunity identification**
- **Location-based business recommendations**

### Interactive Business Intelligence Dashboard
- **Real-time KPI monitoring**
- **Interactive Plotly visualizations**
- **Advanced filtering and date range selection**
- **Professional business theme**
- **Export capabilities**

## 🚀 Production Features (NEW)

### Security & Authentication
- **User Authentication System** - Secure login with role-based access
- **Data Privacy Protection** - Optional data anonymization and encryption
- **Secure File Validation** - Upload security and file type validation
- **Session Management** - Timeout handling and secure sessions

### Performance & Monitoring
- **Memory Usage Monitoring** - Real-time resource tracking with warnings
- **Performance Optimization** - Cloud-optimized processing and caching
- **Health Checks** - System status monitoring and diagnostics
- **Error Handling** - Comprehensive error management and logging

### Enterprise Features
- **Environment Configuration** - Production/development environment separation
- **Audit Logging** - Complete access and operation tracking
- **Data Backup Considerations** - Session-based processing with export capabilities
- **Scalability** - Configurable limits and resource management

## 🚀 Streamlit Cloud Deployment (Recommended)

### Quick Deploy to Streamlit Cloud
1. **Fork/Clone this repository** to your GitHub account
2. **Visit** [Streamlit Cloud](https://share.streamlit.io/)
3. **Connect your GitHub repository**
4. **Set environment variables** (see Environment Configuration below)
5. **Deploy!** Your dashboard will be live at `https://share.streamlit.io/your-username/repo-name`

### Environment Configuration for Production
Set these variables in Streamlit Cloud:
```bash
ENVIRONMENT=production
DEBUG=False
ENABLE_AUTH=True
SECRET_KEY=your-production-secret-key
ANONYMIZE_DATA=True
MAX_FILE_SIZE_MB=200
```

**📚 Complete deployment guide:** See `DEPLOYMENT.md` for detailed instructions.

## 💻 Local Development

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/customer-analytics-dashboard.git
   cd customer-analytics-dashboard
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment (optional):**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

6. **Generate sample data (optional):**
   ```bash
   python generate_sample_data.py
   ```

7. **Run the dashboard:**
   ```bash
   streamlit run app.py
   ```

8. **Open your browser:**
   - The dashboard will open at `http://localhost:8501`

### 🔐 Default Login Credentials (Development)
- **Admin**: `admin` / `admin123`
- **Analyst**: `analyst` / `analyst123`

⚠️ **Change these in production!**

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

### Optional Columns (for Geographic Analysis)

| Column | Type | Description |
|--------|------|-------------|
| `country` | String | Customer's country |
| `region` | String | Customer's region/state |
| `city` | String | Customer's city |

### Sample Data
```csv
customer_id,order_date,product_name,quantity,unit_price,total_amount,country,region,city
C0001,2024-01-15,Wireless Headphones,1,89.99,89.99,United States,California,Los Angeles
C0002,2024-01-16,Coffee Maker,2,79.99,159.98,Canada,Ontario,Toronto
C0001,2024-02-01,Bluetooth Speaker,1,45.99,45.99,United States,California,Los Angeles
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

### Core Dependencies
- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive visualizations
- **Scikit-learn**: Machine learning for advanced segmentation
- **NumPy**: Numerical computing

### Production Enhancements
- **Memory Monitoring**: Real-time usage tracking with psutil
- **Security Features**: File validation, authentication, session management
- **Logging**: Comprehensive audit trails and error tracking
- **Configuration Management**: Environment-based settings
- **Performance Optimization**: Caching, chunked processing, garbage collection

## Project Structure

```
customer-analytics-dashboard/
├── 📱 Core Application
│   ├── app.py                    # Main Streamlit application (ENHANCED)
│   ├── config.py                 # Configuration management (ENHANCED)
│   ├── utils.py                  # Utility functions (NEW)
│   ├── auth.py                   # Authentication system (NEW)
│   ├── brand_config.py          # Brand customization
│   ├── run.py                    # Application runner
│   └── generate_sample_data.py  # Sample data generator
│
├── 📊 Analytics Modules
│   └── modules/
│       ├── __init__.py
│       ├── data_processor.py     # Data loading and validation
│       ├── customer_analytics.py # Customer segmentation logic
│       ├── sales_analytics.py    # Sales performance metrics
│       └── geographic_analytics.py # Geographic analysis
│
├── ⚙️ Configuration & Deployment
│   ├── requirements.txt          # Python dependencies (OPTIMIZED)
│   ├── .env.example             # Environment template (NEW)
│   ├── .streamlit/
│   │   └── config.toml          # Streamlit config (ENHANCED)
│   ├── packages.txt             # System packages (NEW)
│   ├── Dockerfile               # Docker support (NEW)
│   └── .dockerignore            # Docker ignore (NEW)
│
├── 📚 Documentation
│   ├── README.md                # Project documentation (UPDATED)
│   ├── DEPLOYMENT.md            # Deployment guide (NEW)
│   └── PRODUCTION_READY.md      # Production features (NEW)
│
└── 📂 Data
    └── sample_data/             # Generated sample datasets
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

3. **Geographic Analysis**
   - Select "Geographic Analysis" to explore location-based insights
   - Review regional performance and market penetration
   - Identify expansion opportunities and mature markets
   - Analyze geographic customer segments and trends

4. **Advanced Analytics**
   - Go to "Advanced Analytics"
   - Explore cohort analysis for retention insights
   - Review predictive insights and recommendations
   - Identify customers at risk of churning

## 🔧 Configuration Options

### Environment Variables
Create a `.env` file or set in Streamlit Cloud:

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | development | Application environment |
| `ENABLE_AUTH` | False | Enable user authentication |
| `ANONYMIZE_DATA` | False | Enable data anonymization |
| `MAX_FILE_SIZE_MB` | 200 | Maximum upload size |
| `MAX_RECORDS` | 100000 | Maximum records to process |
| `LOG_LEVEL` | INFO | Logging level |

### Security Features
- **Authentication**: Optional user login system
- **Data Privacy**: Configurable data anonymization
- **File Security**: Upload validation and size limits
- **Session Management**: Secure session handling

### Performance Features
- **Memory Monitoring**: Real-time usage tracking
- **Resource Limits**: Configurable processing limits
- **Caching**: Optimized data processing
- **Error Handling**: Comprehensive error management

## 📚 Documentation

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Complete Streamlit Cloud deployment guide
- **[PRODUCTION_READY.md](PRODUCTION_READY.md)** - Production features overview
- **[.env.example](.env.example)** - Environment configuration template

## 🚀 Production Deployment Status

✅ **Ready for Streamlit Cloud**  
✅ **Security Features Implemented**  
✅ **Performance Optimized**  
✅ **Monitoring & Logging**  
✅ **Comprehensive Documentation**  

---

**Ready to deploy?** Follow the [deployment guide](DEPLOYMENT.md) to launch your production-grade Customer Analytics Dashboard on Streamlit Cloud!