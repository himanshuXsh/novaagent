import streamlit as st

from frontend.utils.api_client import API_BASE_URL


def render_file_card(file_data):
    if not file_data:
        return
        
    icon = "📄"
    if file_data["format"] == "pdf":
        icon = "📕"
    elif file_data["format"] == "pptx":
        icon = "📊"
        
    download_url = f"{API_BASE_URL}/agents/documents/download/{file_data['id']}"
    
    st.markdown(f"""
<div class="file-card">
<div class="file-icon">{icon}</div>
<div class="file-details">
<div class="file-title">{file_data['title']}</div>
<div class="file-meta">{file_data['filename']}</div>
</div>
<a href="{download_url}" target="_blank" class="file-download-btn">Download</a>
</div>
    """, unsafe_allow_html=True)
