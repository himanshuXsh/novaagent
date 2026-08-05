import os

import streamlit as st

st.set_page_config(
    page_title="NovaAgent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load global CSS
def load_css(file_name):
    path = os.path.join(os.path.dirname(__file__), "styles", file_name)
    if os.path.exists(path):
        with open(path) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css("theme.css")
load_css("shell.css")
load_css("login.css")
load_css("dashboard.css")
load_css("sidebar.css")
load_css("chat.css")
load_css("coding.css")
load_css("search.css")
load_css("documents.css")
load_css("images.css")
load_css("rag.css")
load_css("billing.css")
load_css("settings.css")

# Check URL params for JWT from OAuth callback
query_params = st.query_params
if "jwt" in query_params:
    st.session_state["jwt"] = query_params.get("jwt")
    # clear params
    st.query_params.clear()

# Simple Routing
if "jwt" not in st.session_state:
    st.switch_page("pages/login.py")
else:
    st.switch_page("pages/dashboard.py")
