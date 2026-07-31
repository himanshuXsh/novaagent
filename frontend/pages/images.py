import streamlit as st
from frontend.components.layout.navbar import render_navbar
from frontend.components.images.image_card import render_image_card
from frontend.utils.api_client import fetch_user_profile, generate_image, fetch_images

if "jwt" not in st.session_state:
    st.switch_page("app.py")

jwt = st.session_state["jwt"]
user = fetch_user_profile(jwt)

if not user:
    st.session_state.clear()
    st.switch_page("app.py")

# Simple Sidebar
st.sidebar.markdown("""
    <div style='text-align: center; margin-bottom: 32px;'>
        <img src='app/static/logo.png' width='50' style='margin-bottom: 8px;' />
        <div style='font-weight: 700; font-size: 20px;'>NovaAgent</div>
    </div>
""", unsafe_allow_html=True)

st.sidebar.page_link("app.py", label="Back to Dashboard", icon="🔙")

# Navbar
render_navbar(user_info=user)

st.markdown("<h2 style='text-align: center; margin-top: 16px; margin-bottom: 32px;'>Image Generator</h2>", unsafe_allow_html=True)

# Main Container
container = st.container()

with container:
    prompt = st.text_input("Describe the image you want to create (e.g. 'A futuristic city at sunset, cyberpunk style')")
    
    if st.button("Generate Image", type="primary"):
        if prompt:
            with st.spinner("Painting..."):
                res = generate_image(jwt, prompt)
                if not res:
                    st.error("Failed to generate image.")
                else:
                    st.rerun() # Refresh to show new image in gallery
        else:
            st.warning("Please enter a prompt.")

st.markdown("<hr style='margin-top: 32px; margin-bottom: 32px;' />", unsafe_allow_html=True)

st.markdown("### Your Gallery")

images = fetch_images(jwt)

if not images:
    st.info("No images generated yet.")
else:
    st.markdown("<div class='image-gallery'>", unsafe_allow_html=True)
    # Streamlit columns can act like a grid, but CSS grid is better. We'll use Streamlit cols for simplicity if needed,
    # or just let CSS grid handle it if we inject raw HTML. Since we have a component that outputs HTML, we can just 
    # output all of them inside a div.
    
    # But `st.markdown` executes sequentially. So we can build a giant HTML string.
    gallery_html = "<div class='image-gallery'>"
    for img in images:
        url = img.get("url")
        p = img.get("prompt", "Generated Image")
        gallery_html += f"""
        <div class="image-card">
            <img src="{url}" alt="{p}" />
            <div class="image-details">
                <div class="image-prompt">"{p}"</div>
                <div class="image-meta">
                    <a href="{url}" target="_blank" class="image-download" download>Download</a>
                </div>
            </div>
        </div>
        """
    gallery_html += "</div>"
    st.markdown(gallery_html, unsafe_allow_html=True)
