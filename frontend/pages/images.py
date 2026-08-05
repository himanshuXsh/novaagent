import streamlit as st

st.set_page_config(layout="wide", initial_sidebar_state="expanded")

from frontend.components.layout.shell import render_sidebar, render_topbar
from frontend.utils.api_client import (
    fetch_balance,
    fetch_images,
    fetch_user_profile,
    generate_image,
    delete_image,
)
import requests
from frontend.utils.css_loader import load_all_css

load_all_css()


def render_images():
    if "jwt" not in st.session_state:
        st.switch_page("app.py")

    jwt = st.session_state["jwt"]
    user = fetch_user_profile(jwt)

    if not user:
        st.session_state.clear()
        st.switch_page("app.py")

    balance = fetch_balance(jwt) or {}
    user_for_shell = {**user, "credits": balance.get("credits")}

    from frontend.utils.api_client import fetch_conversations
    conversations = fetch_conversations(jwt, agent_type="images")

    render_sidebar(active="images", user=user_for_shell, sessions=conversations, on_new_label="New Image", active_session_id=None)
    render_topbar(icon="🖼️", title="Image Generator", subtitle="Create stunning images with AI", user=user_for_shell)
    
    st.markdown("<div class='nova-page-header-spacer'></div>", unsafe_allow_html=True)

    # Let the main content take the full width
    st.markdown("<div class='image-prompt-container'>", unsafe_allow_html=True)
    prompt = st.text_area(
        "Prompt",
        placeholder="A futuristic cityscape at sunset with flying cars and neon lights",
        label_visibility="collapsed",
        height=120,
        key="image_prompt_input"
    )
    
    # Character counter and bottom action row
    st.markdown(f"<div class='char-counter'>{len(prompt) if prompt else 0} / 1000</div>", unsafe_allow_html=True)
    
    btn_col1, btn_col2, btn_col3, btn_col4 = st.columns([1.5, 1.5, 4, 2])
    with btn_col1:
        st.button("✨ Enhance Prompt", key="btn_enhance")
    with btn_col2:
        st.button("🎲 Surprise Me", key="btn_surprise")
    with btn_col4:
        generate_clicked = st.button("✨ Generate", type="primary", use_container_width=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

    if generate_clicked:
        if prompt:
            # Default to 1 image now that settings are removed
            num_images = 1
            
            with st.spinner(f"Painting {num_images} image(s)..."):
                success_count = 0
                for _ in range(num_images):
                    res = generate_image(jwt, prompt)
                    if res and "error" in res:
                        st.error(res["error"])
                    elif res:
                        success_count += 1
                        
                if success_count == 0:
                    st.error("Failed to generate image due to an error.")
                else:
                    st.success(f"Successfully generated {success_count} image(s)!")
                    fetch_images.clear()
                    # No st.rerun() needed, script continues and fetches below
        else:
            st.warning("Please enter a prompt.")


    # ---- YOUR GENERATIONS ----
    st.markdown("<div class='gallery-header'>", unsafe_allow_html=True)
    g_col1, g_col2 = st.columns([3, 1])
    with g_col1:
        st.markdown("<span class='gallery-title'>Your Generations</span>", unsafe_allow_html=True)
    with g_col2:
        st.selectbox("Sort", ["Newest First", "Oldest First"], label_visibility="collapsed", key="sort_gallery")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown(
        "<div class='gallery-filters'>\n"
        "<div class='filter-btn active'>All</div>\n"
        "<div class='filter-btn'>Favorites</div>\n"
        "<div class='filter-btn'>Upscaled</div>\n"
        "</div>",
        unsafe_allow_html=True
    )

    images = fetch_images(jwt) or []

    if not images:
        st.markdown(
            "<div class='empty-state'>\n"
            "<div class='empty-icon'>🖼️</div>\n"
            "<div class='empty-title'>No images generated yet</div>\n"
            "<div class='empty-subtitle'>Type a prompt above and click generate to create your first masterpiece.</div>\n"
            "</div>",
            unsafe_allow_html=True
        )
    else:
        # Create a grid layout with 3 columns
        cols = st.columns(3)
        for i, img in enumerate(images):
            url = img.get("url")
            p = img.get("prompt", "Generated Image")
            art_id = img.get("id")
            
            with cols[i % 3]:
                if url:
                    st.image(url, use_container_width=True, caption=p[:50] + "..." if len(p) > 50 else p)
                else:
                    st.warning("Image URL missing or corrupt.")
                
                try:
                    # Use link_button for downloading to avoid blocking Python with synchronous requests
                    st.link_button(
                        label="⤓ Download",
                        url=url if url else "https://example.com",
                        use_container_width=True,
                        disabled=not url
                    )
                except Exception:
                    pass

                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("🔄 Regenerate", key=f"regen_{art_id}", use_container_width=True):
                        with st.spinner("Regenerating..."):
                            res = generate_image(jwt, p)
                            if res and "error" not in res:
                                st.success("Regenerated successfully!")
                                fetch_images.clear()
                                st.rerun()
                            else:
                                st.error("Failed to regenerate.")
                with col_btn2:
                    if st.button("🗑️ Delete", key=f"del_{art_id}", type="secondary", use_container_width=True):
                        if delete_image(jwt, art_id):
                            st.success("Deleted!")
                            fetch_images.clear()
                            st.rerun()
                        else:
                            st.error("Failed to delete.")
        
        st.markdown("<div class='load-more' style='margin-top: 20px; text-align: center; color: var(--text-secondary); cursor: pointer;'>Load more ⌄</div>", unsafe_allow_html=True)

render_images()
