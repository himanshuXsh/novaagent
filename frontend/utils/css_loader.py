import os

import streamlit as st


@st.cache_data
def load_all_css():
    """Load all global CSS styles. Must be called on every page."""
    css_files = [
        "theme.css", "shell.css", "login.css", "dashboard.css", "sidebar.css",
        "chat.css", "coding.css", "search.css", "documents.css",
        "images.css", "rag.css", "billing.css", "settings.css"
    ]
    styles_dir = os.path.join(os.path.dirname(__file__), "..", "styles")
    combined = ""
    for f in css_files:
        path = os.path.join(styles_dir, f)
        if os.path.exists(path):
            with open(path) as fp:
                combined += fp.read() + "\n"
    if combined:
        st.markdown(f"<style>{combined}</style>", unsafe_allow_html=True)
