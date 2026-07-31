import streamlit as st
from frontend.components.chat.sidebar import render_chat_sidebar
from frontend.components.chat.message_renderer import render_message
from frontend.components.layout.navbar import render_navbar
from frontend.components.coding.artifact_panel import render_artifact_panel
from frontend.utils.api_client import fetch_user_profile, fetch_conversations, fetch_messages, generate_code

if "jwt" not in st.session_state:
    st.switch_page("app.py")

jwt = st.session_state["jwt"]
user = fetch_user_profile(jwt)

if not user:
    st.session_state.clear()
    st.switch_page("app.py")

if "coding_conv_id" not in st.session_state:
    st.session_state["coding_conv_id"] = None
    
if "coding_messages" not in st.session_state or st.session_state["coding_messages"] is None:
    if st.session_state["coding_conv_id"]:
        st.session_state["coding_messages"] = fetch_messages(jwt, st.session_state["coding_conv_id"])
    else:
        st.session_state["coding_messages"] = []
        
if "current_artifact" not in st.session_state:
    st.session_state["current_artifact"] = None

# Filter for only coding conversations in sidebar
all_convs = fetch_conversations(jwt)
coding_convs = [c for c in all_convs if c.get("agent_type") == "coding"]

# Layout Sidebar (we can reuse chat sidebar but pass coding_conv_id state name via session state if we modify it, 
# but currently sidebar hardcodes 'current_conv_id'. For simplicity, let's just let it be, but we should 
# ideally sync it. Actually, `sidebar.py` uses `st.session_state["current_conv_id"]` which might conflict with chat.
# To keep it simple, we will use the same state keys but we shouldn't mix conversations.
# Let's map it manually for now)

# Let's override sidebar state keys inside sidebar or just rely on a new sidebar. 
# We'll build a quick custom sidebar for coding to avoid state conflicts:
st.sidebar.markdown("""
    <div style='text-align: center; margin-bottom: 32px;'>
        <img src='app/static/logo.png' width='50' style='margin-bottom: 8px;' />
        <div style='font-weight: 700; font-size: 20px;'>NovaAgent</div>
    </div>
""", unsafe_allow_html=True)

st.sidebar.page_link("app.py", label="Back to Dashboard", icon="🔙")

if st.sidebar.button("+ New Coding Session", use_container_width=True, type="primary"):
    st.session_state["coding_conv_id"] = None
    st.session_state["coding_messages"] = []
    st.session_state["current_artifact"] = None
    st.rerun()
    
st.sidebar.markdown("<div style='margin-top: 24px; font-size: 12px; font-weight: 600; color: var(--text-secondary); margin-bottom: 8px;'>Recent Code Sessions</div>", unsafe_allow_html=True)

for conv in coding_convs:
    is_active = conv["id"] == st.session_state["coding_conv_id"]
    if st.sidebar.button(f"💻 {conv['title']}", key=f"coding_conv_{conv['id']}", use_container_width=True):
        st.session_state["coding_conv_id"] = conv["id"]
        st.session_state["coding_messages"] = fetch_messages(jwt, conv["id"])
        st.session_state["current_artifact"] = None # Reset artifact view on load
        st.rerun()

# Navbar
render_navbar(user_info=user)
st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

# Main Grid (Split Pane)
chat_col, artifact_col = st.columns([1, 1])

with chat_col:
    st.markdown("### Coding Agent")
    messages_container = st.container(height=600, border=False)
    
    with messages_container:
        for msg in st.session_state["coding_messages"]:
            render_message(msg["role"], msg["content"])

with artifact_col:
    render_artifact_panel(st.session_state.get("current_artifact"))

# Input
if prompt := st.chat_input("Ask for a script, component, or code review..."):
    st.session_state["coding_messages"].append({"role": "user", "content": prompt})
    
    with chat_col:
        with messages_container:
            render_message("user", prompt)
            with st.spinner("Writing code..."):
                resp = generate_code(jwt, prompt, st.session_state["coding_conv_id"])
                
                if resp:
                    if not st.session_state["coding_conv_id"]:
                        st.session_state["coding_conv_id"] = resp.get("conversation_id")
                        
                    st.session_state["coding_messages"].append({
                        "role": "assistant", 
                        "content": resp.get("text_content")
                    })
                    
                    if resp.get("code"):
                        st.session_state["current_artifact"] = {
                            "language": resp.get("language"),
                            "code": resp.get("code")
                        }
                    st.rerun()
                else:
                    st.error("Failed to generate code.")
