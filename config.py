"""
Configuration settings for the Customer Analytics Dashboard
"""

import os
import logging
import streamlit as st
from pathlib import Path
from typing import Dict, Any

class Config:
    """Application configuration settings"""
    
    # App metadata
    APP_NAME = "Customer Analytics Dashboard"
    APP_VERSION = "1.0.0"
    APP_DESCRIPTION = "Advanced e-commerce customer intelligence platform"
    
    # Environment detection
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Streamlit configuration
    STREAMLIT_PORT = int(os.getenv('PORT', 8501))
    STREAMLIT_HOST = os.getenv('HOST', '0.0.0.0')
    
    # Performance settings
    MAX_RECORDS = int(os.getenv('MAX_RECORDS', 100000))
    CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', 10000))
    CACHE_TTL = int(os.getenv('CACHE_TTL', 3600))  # 1 hour
    MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', 200))
    MAX_MEMORY_USAGE_MB = int(os.getenv('MAX_MEMORY_USAGE_MB', 1000))
    
    # Security settings
    ENABLE_AUTH = os.getenv('ENABLE_AUTH', 'False').lower() == 'true'
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', 3600))  # 1 hour
    
    # Data privacy
    ANONYMIZE_DATA = os.getenv('ANONYMIZE_DATA', 'False').lower() == 'true'
    DATA_RETENTION_DAYS = int(os.getenv('DATA_RETENTION_DAYS', 90))
    ENABLE_DATA_ENCRYPTION = os.getenv('ENABLE_DATA_ENCRYPTION', 'False').lower() == 'true'
    
    # Logging configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE = os.getenv('LOG_FILE', 'app.log')
    ENABLE_FILE_LOGGING = os.getenv('ENABLE_FILE_LOGGING', 'True').lower() == 'true'
    
    # Monitoring and analytics
    ENABLE_TELEMETRY = os.getenv('ENABLE_TELEMETRY', 'False').lower() == 'true'
    ANALYTICS_ENDPOINT = os.getenv('ANALYTICS_ENDPOINT', '')
    HEALTH_CHECK_INTERVAL = int(os.getenv('HEALTH_CHECK_INTERVAL', 300))  # 5 minutes
    
    # Error handling
    SENTRY_DSN = os.getenv('SENTRY_DSN', '')
    ENABLE_ERROR_REPORTING = bool(SENTRY_DSN)
    
    # Analytics settings
    RFM_QUANTILES = 5
    DEFAULT_SEGMENTS = [
        'Champions', 'Loyal Customers', 'Potential Loyalists', 
        'New Customers', 'At Risk', 'Cannot Lose Them', 
        'Hibernating', 'Lost Customers'
    ]
    
    # Visualization settings
    CHART_COLORS = {
        'primary': '#1f77b4',
        'secondary': '#17a2b8', 
        'success': '#28a745',
        'warning': '#ffc107',
        'danger': '#dc3545',
        'info': '#6c757d'
    }
    
    SEGMENT_COLORS = {
        'Champions': '#28a745',
        'Loyal Customers': '#17a2b8',
        'Potential Loyalists': '#ffc107',
        'New Customers': '#6f42c1',
        'At Risk': '#fd7e14',
        'Cannot Lose Them': '#dc3545',
        'Hibernating': '#6c757d',
        'Lost Customers': '#343a40'
    }
    
    # Data validation rules
    REQUIRED_COLUMNS = [
        'customer_id', 'order_date', 'product_name',
        'quantity', 'unit_price', 'total_amount'
    ]
    
    COLUMN_TYPES = {
        'customer_id': 'string',
        'order_date': 'datetime',
        'product_name': 'string',
        'quantity': 'numeric',
        'unit_price': 'numeric',
        'total_amount': 'numeric'
    }
    
    # Error messages
    ERROR_MESSAGES = {
        'missing_columns': "Missing required columns. Please ensure your CSV contains: {}",
        'invalid_data': "Invalid data detected. Please check data quality and try again.",
        'processing_error': "Error processing data. Please verify file format and content.",
        'insufficient_data': "Insufficient data for analysis. Minimum 100 records required.",
        'date_format': "Invalid date format. Expected format: YYYY-MM-DD",
        'numeric_validation': "Non-numeric values found in numeric columns."
    }
    
    # Success messages
    SUCCESS_MESSAGES = {
        'data_loaded': "✅ Data loaded successfully: {:,} records processed",
        'analysis_complete': "✅ Analysis completed successfully",
        'export_complete': "✅ Data exported successfully"
    }
    
    # File settings
    ALLOWED_EXTENSIONS = ['csv']
    MAX_FILE_SIZE = MAX_FILE_SIZE_MB * 1024 * 1024  # Convert MB to bytes
    
    # Export settings
    EXPORT_FORMATS = ['csv', 'excel']
    
    @classmethod
    def get_streamlit_config(cls):
        """Get Streamlit-specific configuration"""
        return {
            'page_title': cls.APP_NAME,
            'page_icon': '📊',
            'layout': 'wide',
            'initial_sidebar_state': 'expanded'
        }
    
    @classmethod
    def get_chart_config(cls, chart_type: str = 'default'):
        """Get chart configuration for consistent styling"""
        base_config = {
            'displayModeBar': False,
            'staticPlot': False,
            'responsive': True
        }
        
        if chart_type == 'interactive':
            base_config.update({
                'displayModeBar': True,
                'modeBarButtonsToRemove': [
                    'pan2d', 'lasso2d', 'select2d', 'autoScale2d'
                ]
            })
        
        return base_config
    
    @classmethod
    def get_logging_config(cls) -> Dict[str, Any]:
        """Get logging configuration"""
        config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    'format': cls.LOG_FORMAT
                },
            },
            'handlers': {
                'console': {
                    'level': cls.LOG_LEVEL,
                    'class': 'logging.StreamHandler',
                    'formatter': 'standard',
                },
            },
            'loggers': {
                '': {
                    'handlers': ['console'],
                    'level': cls.LOG_LEVEL,
                    'propagate': False
                }
            }
        }
        
        if cls.ENABLE_FILE_LOGGING:
            config['handlers']['file'] = {
                'level': cls.LOG_LEVEL,
                'class': 'logging.FileHandler',
                'filename': cls.LOG_FILE,
                'formatter': 'standard',
            }
            config['loggers']['']['handlers'].append('file')
        
        return config
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production environment"""
        return cls.ENVIRONMENT.lower() == 'production'
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate configuration settings"""
        errors = []
        
        if cls.is_production():
            if cls.SECRET_KEY == 'your-secret-key-change-in-production':
                errors.append("SECRET_KEY must be changed in production")
            
            if cls.DEBUG:
                errors.append("DEBUG should be False in production")
            
            if not cls.ENABLE_AUTH and cls.ENVIRONMENT == 'production':
                errors.append("Authentication should be enabled in production")
        
        if errors:
            for error in errors:
                logging.error(f"Configuration error: {error}")
            return False
        
        return True

class ErrorHandler:
    """Centralized error handling"""
    
    @staticmethod
    def handle_data_error(error: Exception, operation: str = "data processing"):
        """Handle data-related errors with user-friendly messages"""
        error_msg = str(error).lower()
        
        if 'memory' in error_msg:
            st.error(f"❌ Memory error during {operation}. Try with a smaller dataset.")
        elif 'permission' in error_msg:
            st.error(f"❌ Permission denied. Check file access rights.")
        elif 'file not found' in error_msg:
            st.error(f"❌ File not found. Please verify file path.")
        elif 'parse' in error_msg or 'decode' in error_msg:
            st.error(f"❌ File parsing error. Please check file format and encoding.")
        else:
            st.error(f"❌ Error during {operation}: {str(error)}")
    
    @staticmethod
    def handle_analysis_error(error: Exception, analysis_type: str = "analysis"):
        """Handle analysis-related errors"""
        st.error(f"❌ Error in {analysis_type}: {str(error)}")
        st.info("Please check your data quality and try again.")
    
    @staticmethod
    def handle_visualization_error(error: Exception):
        """Handle visualization errors"""
        st.error(f"❌ Visualization error: {str(error)}")
        st.info("Unable to generate chart. Please verify your data.")

class ValidationRules:
    """Data validation rules and constraints"""
    
    @staticmethod
    def validate_numeric_range(value, min_val=None, max_val=None):
        """Validate numeric values within range"""
        if min_val is not None and value < min_val:
            return False
        if max_val is not None and value > max_val:
            return False
        return True
    
    @staticmethod
    def validate_date_range(date, min_date=None, max_date=None):
        """Validate date values within range"""
        if min_date is not None and date < min_date:
            return False
        if max_date is not None and date > max_date:
            return False
        return True
    
    @staticmethod
    def get_business_rules():
        """Get business-specific validation rules"""
        from datetime import datetime, timedelta
        
        return {
            'quantity': {'min': 0, 'max': 1000},
            'unit_price': {'min': 0.01, 'max': 10000},
            'total_amount': {'min': 0.01, 'max': 100000},
            'order_date': {
                'min': datetime(2020, 1, 1),
                'max': datetime.now() + timedelta(days=1)
            }
        }