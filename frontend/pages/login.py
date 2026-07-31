import streamlit as st
import base64
from frontend.utils.api_client import get_google_login_url

def render_login():
    st.markdown("""
        <div class="login-container">
            <div class="login-card">
                <img src="app/static/logo.png" width="80" class="login-logo" />
                <div class="login-title">Welcome to NovaAgent</div>
                <div class="login-subtitle">Your Intelligent Multi-Agent AI Workspace</div>
    """, unsafe_allow_html=True)
    
    login_url = get_google_login_url()
    st.markdown(f"""
        <a href="{login_url}" target="_self" style="text-decoration: none;">
            <button class="stButton btn-google">Continue with Google</button>
        </a>
    """, unsafe_allow_html=True)

    st.markdown("""
            </div>
        </div>
    """, unsafe_allow_html=True)

render_login()
