"""
Authentication utilities for user login
"""

import json
import streamlit as st
from typing import Dict, Optional, Tuple


class AuthManager:
    """Handles user authentication and session management"""
    
    def __init__(self, users_config_path: str = "users_config.json"):
        self.users_config_path = users_config_path
        self.users = self._load_users()
    
    def _load_users(self) -> Dict:
        """Load user configurations from Streamlit secrets or JSON file"""
        try:
            # Try Streamlit secrets first (for cloud deployment)
            if hasattr(st, 'secrets') and 'users' in st.secrets:
                return dict(st.secrets['users'])
        except Exception:
            pass
        
        # Fallback to JSON file (for local development)
        try:
            with open(self.users_config_path, 'r') as f:
                config = json.load(f)
                return config.get('users', {})
        except FileNotFoundError:
            st.error(f"Users configuration not found")
            return {}
        except json.JSONDecodeError:
            st.error("Invalid JSON in users configuration file")
            return {}
    
    def authenticate_user(self, username: str, password: str) -> Tuple[bool, Optional[str]]:
        """
        Authenticate user credentials
        
        Args:
            username: Username to authenticate
            password: Password to verify
            
        Returns:
            Tuple of (is_authenticated, role)
        """
        if username in self.users:
            user_data = self.users[username]
            if user_data.get('password') == password:
                return True, user_data.get('role', 'user')
        
        return False, None
    
    def is_logged_in(self) -> bool:
        """Check if user is currently logged in"""
        return st.session_state.get('authenticated', False)
    
    def get_current_user(self) -> Optional[str]:
        """Get current logged in username"""
        return st.session_state.get('username')
    
    def get_current_user_role(self) -> Optional[str]:
        """Get current logged in user's role"""
        return st.session_state.get('user_role')
    
    def login_user(self, username: str, role: str):
        """Set user as logged in"""
        st.session_state.authenticated = True
        st.session_state.username = username
        st.session_state.user_role = role
    
    def logout_user(self):
        """Log out current user and clear session"""
        # Clear all session state except login-related
        keys_to_keep = []
        for key in list(st.session_state.keys()):
            if key not in keys_to_keep:
                del st.session_state[key]
        
        st.session_state.authenticated = False
    
    def show_login_page(self):
        """Display the login page"""
        st.set_page_config(
            page_title="ID Generator - Login",
            page_icon="🔐",
            layout="centered"
        )
        
        # Center the login form
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.title("Login")
            st.markdown("Enter credentials:")
            
            # Login form
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                login_button = st.form_submit_button("Login", width="stretch")
                
                if login_button:
                    if not username or not password:
                        st.error("Please enter both username and password")
                    else:
                        is_authenticated, role = self.authenticate_user(username, password)
                        
                        if is_authenticated:
                            self.login_user(username, role)
                            st.success(f"Welcome, {username}!")
                            st.rerun()
                        else:
                            st.error("Invalid username or password")
            
            st.markdown("---")
            st.markdown("*Contact administrator for access*")
    