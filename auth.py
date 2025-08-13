import streamlit as st
import time
import logging
from typing import Optional, Dict, Any
from utils import SecurityUtils, AuthenticationManager
from config import Config

logger = logging.getLogger(__name__)

def show_login_page():
    """Display login page with authentication form"""
    st.markdown("""
    <div style="
        max-width: 400px; 
        margin: 100px auto; 
        padding: 2rem; 
        border-radius: 10px; 
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        background: white;
    ">
    """, unsafe_allow_html=True)
    
    st.markdown("### 🔐 Customer Analytics Dashboard")
    st.markdown("Please log in to access the dashboard")
    
    with st.form("login_form"):
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        submit_button = st.form_submit_button("Login", use_container_width=True)
        
        if submit_button:
            if username and password:
                if AuthenticationManager.authenticate_user(username, password):
                    st.success("✅ Login successful!")
                    time.sleep(1)  # Brief pause for user feedback
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")
                    # Add rate limiting in production
                    time.sleep(2)  # Prevent brute force attacks
            else:
                st.error("❌ Please enter both username and password")
    
    # Demo credentials info (remove in production)
    if not Config.is_production():
        st.markdown("---")
        st.markdown("**Demo Credentials:**")
        st.code("Username: admin | Password: admin123")
        st.code("Username: analyst | Password: analyst123")
        st.caption("⚠️ Change these credentials in production!")
    
    st.markdown("</div>", unsafe_allow_html=True)

def show_logout_button():
    """Display logout button in sidebar"""
    with st.sidebar:
        st.markdown("---")
        col1, col2 = st.columns([3, 1])
        
        with col1:
            if 'username' in st.session_state:
                st.caption(f"👤 Logged in as: **{st.session_state.username}**")
        
        with col2:
            if st.button("Logout", help="Click to logout"):
                AuthenticationManager.logout()
                st.rerun()

def check_session_timeout():
    """Check if user session has expired"""
    if Config.ENABLE_AUTH and 'session_start' in st.session_state:
        session_age = time.time() - st.session_state.session_start
        if session_age > Config.SESSION_TIMEOUT:
            st.warning("⏰ Session expired. Please log in again.")
            AuthenticationManager.logout()
            st.rerun()

def require_authentication():
    """Main authentication wrapper for the application"""
    if not Config.ENABLE_AUTH:
        return True
    
    # Check session timeout
    check_session_timeout()
    
    # Check if user is authenticated
    if not AuthenticationManager.check_authentication():
        show_login_page()
        st.stop()
    
    # Show logout button for authenticated users
    show_logout_button()
    return True

def init_auth_session():
    """Initialize authentication session state"""
    if 'auth_initialized' not in st.session_state:
        st.session_state.auth_initialized = True
        
        # Set default values
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        
        logger.info("Authentication session initialized")

# Role-based access control (for future expansion)
class RoleManager:
    """Manage user roles and permissions"""
    
    ROLES = {
        'admin': {
            'permissions': ['view_all', 'edit_all', 'delete_data', 'manage_users'],
            'description': 'Full system access'
        },
        'analyst': {
            'permissions': ['view_all', 'export_data'],
            'description': 'View and analyze data'
        },
        'viewer': {
            'permissions': ['view_basic'],
            'description': 'Basic view access'
        }
    }
    
    @staticmethod
    def get_user_role(username: str) -> str:
        """Get user role (simplified - in production, this would query a database)"""
        role_mapping = {
            'admin': 'admin',
            'analyst': 'analyst'
        }
        return role_mapping.get(username, 'viewer')
    
    @staticmethod
    def has_permission(username: str, permission: str) -> bool:
        """Check if user has specific permission"""
        user_role = RoleManager.get_user_role(username)
        return permission in RoleManager.ROLES.get(user_role, {}).get('permissions', [])
    
    @staticmethod
    def require_permission(permission: str):
        """Decorator to require specific permission"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                if Config.ENABLE_AUTH:
                    username = st.session_state.get('username', '')
                    if not RoleManager.has_permission(username, permission):
                        st.error(f"❌ Permission denied. Required permission: {permission}")
                        st.stop()
                return func(*args, **kwargs)
            return wrapper
        return decorator