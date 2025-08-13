import logging
import hashlib
import secrets
import time
import psutil
import streamlit as st
from typing import Optional, Dict, Any, Callable
from functools import wraps
from config import Config

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format=Config.LOG_FORMAT,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(Config.LOG_FILE) if Config.ENABLE_FILE_LOGGING else None
    ] if Config.ENABLE_FILE_LOGGING else [logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

class SecurityUtils:
    """Security utilities for data protection and user authentication"""
    
    @staticmethod
    def generate_session_token() -> str:
        """Generate secure session token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def hash_data(data: str) -> str:
        """Hash sensitive data using SHA-256"""
        return hashlib.sha256(data.encode()).hexdigest()
    
    @staticmethod
    def anonymize_customer_id(customer_id: str) -> str:
        """Anonymize customer ID for privacy"""
        if Config.ANONYMIZE_DATA:
            return f"ANON_{hashlib.md5(customer_id.encode()).hexdigest()[:8]}"
        return customer_id
    
    @staticmethod
    def validate_file_upload(uploaded_file) -> tuple[bool, str]:
        """Validate uploaded file for security"""
        if not uploaded_file:
            return False, "No file uploaded"
        
        # Check file extension
        file_extension = uploaded_file.name.split('.')[-1].lower()
        if file_extension not in Config.ALLOWED_EXTENSIONS:
            return False, f"File type '{file_extension}' not allowed"
        
        # Check file size
        if uploaded_file.size > Config.MAX_FILE_SIZE:
            max_mb = Config.MAX_FILE_SIZE / (1024 * 1024)
            return False, f"File size exceeds {max_mb:.1f}MB limit"
        
        return True, "File validation passed"

class PerformanceMonitor:
    """Monitor application performance and resource usage"""
    
    @staticmethod
    def get_memory_usage() -> Dict[str, float]:
        """Get current memory usage"""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            'rss_mb': memory_info.rss / 1024 / 1024,
            'vms_mb': memory_info.vms / 1024 / 1024,
            'percent': process.memory_percent()
        }
    
    @staticmethod
    def check_memory_threshold() -> bool:
        """Check if memory usage is within limits"""
        memory_usage = PerformanceMonitor.get_memory_usage()
        return memory_usage['rss_mb'] < Config.MAX_MEMORY_USAGE_MB
    
    @staticmethod
    def log_performance_metrics(operation: str, duration: float, memory_before: Dict, memory_after: Dict):
        """Log performance metrics for monitoring"""
        memory_delta = memory_after['rss_mb'] - memory_before['rss_mb']
        
        logger.info(
            f"Performance - Operation: {operation}, "
            f"Duration: {duration:.2f}s, "
            f"Memory Delta: {memory_delta:.2f}MB, "
            f"Final Memory: {memory_after['rss_mb']:.2f}MB"
        )
        
        if Config.ENABLE_TELEMETRY and Config.ANALYTICS_ENDPOINT:
            # Send metrics to monitoring endpoint
            pass

def performance_monitor(operation_name: str):
    """Decorator to monitor function performance"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            memory_before = PerformanceMonitor.get_memory_usage()
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                logger.error(f"Error in {operation_name}: {str(e)}")
                raise
            finally:
                end_time = time.time()
                memory_after = PerformanceMonitor.get_memory_usage()
                duration = end_time - start_time
                
                PerformanceMonitor.log_performance_metrics(
                    operation_name, duration, memory_before, memory_after
                )
                
                # Check memory threshold
                if not PerformanceMonitor.check_memory_threshold():
                    logger.warning(f"Memory usage exceeded threshold after {operation_name}")
                    st.warning("⚠️ High memory usage detected. Consider using a smaller dataset.")
        
        return wrapper
    return decorator

def safe_execute(func: Callable, operation_name: str = "operation", default_return=None):
    """Safely execute functions with comprehensive error handling"""
    try:
        return func()
    except MemoryError:
        logger.error(f"Memory error during {operation_name}")
        st.error(f"❌ Out of memory during {operation_name}. Please try with a smaller dataset.")
        return default_return
    except FileNotFoundError as e:
        logger.error(f"File not found during {operation_name}: {str(e)}")
        st.error(f"❌ File not found: {str(e)}")
        return default_return
    except PermissionError as e:
        logger.error(f"Permission error during {operation_name}: {str(e)}")
        st.error(f"❌ Permission denied: {str(e)}")
        return default_return
    except ValueError as e:
        logger.error(f"Value error during {operation_name}: {str(e)}")
        st.error(f"❌ Invalid data format: {str(e)}")
        return default_return
    except Exception as e:
        logger.error(f"Unexpected error during {operation_name}: {str(e)}")
        st.error(f"❌ An unexpected error occurred during {operation_name}: {str(e)}")
        
        if Config.ENABLE_ERROR_REPORTING and Config.SENTRY_DSN:
            # Send error to Sentry or other error reporting service
            pass
        
        return default_return

class DataPrivacy:
    """Handle data privacy and compliance requirements"""
    
    @staticmethod
    def apply_privacy_filters(df):
        """Apply privacy filters to sensitive data"""
        if Config.ANONYMIZE_DATA:
            df['customer_id'] = df['customer_id'].apply(SecurityUtils.anonymize_customer_id)
        return df
    
    @staticmethod
    def log_data_access(user_id: str, data_type: str, action: str):
        """Log data access for audit trails"""
        logger.info(
            f"Data Access - User: {user_id}, "
            f"Type: {data_type}, "
            f"Action: {action}, "
            f"Timestamp: {time.time()}"
        )

class AuthenticationManager:
    """Handle user authentication and session management"""
    
    @staticmethod
    def check_authentication() -> bool:
        """Check if user is authenticated"""
        if not Config.ENABLE_AUTH:
            return True
        
        # Check session
        if 'authenticated' not in st.session_state:
            return False
        
        # Check session timeout
        if 'session_start' in st.session_state:
            session_age = time.time() - st.session_state.session_start
            if session_age > Config.SESSION_TIMEOUT:
                st.session_state.clear()
                return False
        
        return st.session_state.get('authenticated', False)
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> bool:
        """Authenticate user with username/password"""
        # Simple authentication for demo - replace with proper auth system
        valid_users = {
            'admin': 'admin123',  # Change in production
            'analyst': 'analyst123'
        }
        
        if username in valid_users and valid_users[username] == password:
            st.session_state.authenticated = True
            st.session_state.username = username
            st.session_state.session_start = time.time()
            st.session_state.session_token = SecurityUtils.generate_session_token()
            
            logger.info(f"User authenticated: {username}")
            return True
        
        logger.warning(f"Failed authentication attempt for user: {username}")
        return False
    
    @staticmethod
    def logout():
        """Logout user and clear session"""
        username = st.session_state.get('username', 'Unknown')
        st.session_state.clear()
        logger.info(f"User logged out: {username}")

def require_auth(func: Callable):
    """Decorator to require authentication for functions"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not AuthenticationManager.check_authentication():
            st.error("🔒 Authentication required")
            st.stop()
        return func(*args, **kwargs)
    return wrapper

class HealthCheck:
    """Application health monitoring"""
    
    @staticmethod
    def check_system_health() -> Dict[str, Any]:
        """Perform comprehensive system health check"""
        health_status = {
            'status': 'healthy',
            'timestamp': time.time(),
            'checks': {}
        }
        
        # Memory check
        memory_usage = PerformanceMonitor.get_memory_usage()
        memory_healthy = memory_usage['rss_mb'] < Config.MAX_MEMORY_USAGE_MB
        health_status['checks']['memory'] = {
            'status': 'pass' if memory_healthy else 'fail',
            'usage_mb': memory_usage['rss_mb'],
            'limit_mb': Config.MAX_MEMORY_USAGE_MB
        }
        
        # Configuration check
        config_valid = Config.validate_config()
        health_status['checks']['configuration'] = {
            'status': 'pass' if config_valid else 'fail'
        }
        
        # Overall status
        all_checks_pass = all(
            check['status'] == 'pass' 
            for check in health_status['checks'].values()
        )
        health_status['status'] = 'healthy' if all_checks_pass else 'unhealthy'
        
        return health_status
    
    @staticmethod
    def log_health_check():
        """Log health check results"""
        health = HealthCheck.check_system_health()
        logger.info(f"Health Check - Status: {health['status']}")
        
        for check_name, check_result in health['checks'].items():
            logger.info(f"Health Check - {check_name}: {check_result['status']}")

# Initialize health monitoring
if Config.HEALTH_CHECK_INTERVAL > 0:
    # In a production environment, this would be handled by a background task
    pass