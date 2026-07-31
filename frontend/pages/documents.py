import streamlit as st
from frontend.components.layout.navbar import render_navbar
from frontend.components.documents.file_card import render_file_card
from frontend.utils.api_client import fetch_user_profile, generate_document, fetch_documents

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

st.markdown("<h2 style='text-align: center; margin-top: 16px; margin-bottom: 32px;'>Document Generator</h2>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### Generate New File")
    doc_format = st.radio("Format", ["PDF Report", "PowerPoint Presentation"], horizontal=True)
    prompt = st.text_area("Describe the content you want to generate:", height=150)
    
    if st.button("Generate File", type="primary"):
        if prompt:
            fmt = "pdf" if doc_format == "PDF Report" else "ppt"
            with st.spinner(f"Generating {fmt.upper()}..."):
                res = generate_document(jwt, prompt, fmt)
                if res:
                    st.success("File generated successfully!")
                else:
                    st.error("Failed to generate file.")
        else:
            st.warning("Please enter a prompt.")

with col2:
    st.markdown("### Your Files")
    files = fetch_documents(jwt)
    if not files:
        st.info("No files generated yet.")
    else:
        # Show most recent first
        for f in reversed(files):
            render_file_card(f)
            st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)
