import streamlit as st

def render_chat_sidebar(conversations, current_conv_id=None):
    st.sidebar.markdown("""
        <div style='text-align: center; margin-bottom: 32px;'>
            <img src='app/static/logo.png' width='50' style='margin-bottom: 8px;' />
            <div style='font-weight: 700; font-size: 20px;'>NovaAgent</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.page_link("app.py", label="Back to Dashboard", icon="🔙")
    
    if st.sidebar.button("+ New Chat", use_container_width=True, type="primary"):
        st.session_state["current_conv_id"] = None
        st.session_state["messages"] = []
        st.rerun()
        
    st.sidebar.markdown("<div style='margin-top: 24px; font-size: 12px; font-weight: 600; color: var(--text-secondary); margin-bottom: 8px;'>Recent Chats</div>", unsafe_allow_html=True)
    
    for conv in conversations:
        is_active = conv["id"] == current_conv_id
        active_class = "active" if is_active else ""
        icon = "💬"
        if conv["agent_type"] == "coding": icon = "💻"
        elif conv["agent_type"] == "search": icon = "🔍"
        
        # We use a button so it can be clicked to load the conversation
        if st.sidebar.button(f"{icon} {conv['title']}", key=f"conv_{conv['id']}", use_container_width=True):
            st.session_state["current_conv_id"] = conv["id"]
            st.session_state["messages"] = None # Force reload
            st.rerun()
