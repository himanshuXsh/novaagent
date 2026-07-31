import streamlit as st

def render_image_card(image_data):
    if not image_data:
        return
        
    url = image_data.get("url")
    prompt = image_data.get("prompt", "Generated Image")
    
    st.markdown(f"""
        <div class="image-card">
            <img src="{url}" alt="{prompt}" />
            <div class="image-details">
                <div class="image-prompt">"{prompt}"</div>
                <div class="image-meta">
                    <span>Generated just now</span>
                    <a href="{url}" target="_blank" class="image-download" download>Download</a>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
