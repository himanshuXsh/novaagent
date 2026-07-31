import streamlit as st

def render_sidebar():
    st.sidebar.markdown("""
        <div style='text-align: center; margin-bottom: 32px;'>
            <img src='app/static/logo.png' width='50' style='margin-bottom: 8px;' />
            <div style='font-weight: 700; font-size: 20px;'>NovaAgent</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Nav items
    st.sidebar.page_link("app.py", label="Dashboard", icon="📊")
    st.sidebar.page_link("pages/chat.py", label="Chat Workspace", icon="💬")
    st.sidebar.page_link("pages/coding.py", label="Coding Agent", icon="💻")
    st.sidebar.page_link("pages/search.py", label="Search Agent", icon="🔍")
    st.sidebar.page_link("pages/documents.py", label="Document Agent", icon="📄")
    st.sidebar.page_link("pages/images.py", label="Image Agent", icon="🎨")
    st.sidebar.page_link("pages/rag.py", label="RAG Agent", icon="📚")
    st.sidebar.page_link("pages/billing.py", label="Billing & Credits", icon="💳")
    
    st.sidebar.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.sidebar.markdown("""
        <div style="padding: 0 16px 8px 16px; font-size: 12px; font-weight: 600; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.5px;">Account</div>
    """, unsafe_allow_html=True)
    st.sidebar.page_link("pages/settings.py", label="Settings", icon="⚙️")
    st.sidebar.markdown("""
        <div style='background-color: var(--bg-primary); padding: 16px; border-radius: var(--radius-button); text-align: center; border: 1px solid var(--border);'>
            <div style='font-size: 14px; color: var(--text-secondary); margin-bottom: 4px;'>Credits Balance</div>
            <div style='font-size: 24px; font-weight: 700; color: var(--success);'>240</div>
        </div>
    """, unsafe_allow_html=True)
