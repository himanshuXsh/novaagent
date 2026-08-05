import streamlit as st

st.set_page_config(layout="wide", initial_sidebar_state="expanded")

from frontend.components.chat.message_renderer import render_message
from frontend.components.layout.shell import render_sidebar, render_topbar
from frontend.utils.api_client import (
    fetch_balance,
    fetch_conversations,
    fetch_messages,
    fetch_user_profile,
    generate_code,
)
from frontend.utils.css_loader import load_all_css

load_all_css()

AGENT_KEY = "coding"

if "jwt" not in st.session_state:
    st.switch_page("app.py")

jwt = st.session_state["jwt"]
user = fetch_user_profile(jwt)

if not user:
    st.session_state.clear()
    st.switch_page("app.py")

balance = fetch_balance(jwt) or {}
user_for_shell = {**user, "credits": balance.get("credits")}

conv_key = f"{AGENT_KEY}_conv_id"
msgs_key = f"{AGENT_KEY}_messages"

if conv_key not in st.session_state:
    st.session_state[conv_key] = None

if msgs_key not in st.session_state or st.session_state[msgs_key] is None:
    if st.session_state[conv_key]:
        st.session_state[msgs_key] = fetch_messages(jwt, st.session_state[conv_key])
    else:
        st.session_state[msgs_key] = []

if "current_artifact" not in st.session_state:
    st.session_state["current_artifact"] = None

all_convs = fetch_conversations(jwt) or []
coding_convs = [c for c in all_convs if c.get("agent_type") == "coding"]

render_sidebar(
    active=AGENT_KEY, user=user_for_shell, sessions=coding_convs,
    on_new_label="New Coding Session", active_session_id=st.session_state[conv_key],
)

render_topbar(icon="💻", title="Coding Agent", subtitle="Your AI pair programmer", user=user_for_shell)
st.markdown("<div class='nova-page-header-spacer'></div>", unsafe_allow_html=True)

messages_container = st.container(height=560, border=False)

with messages_container:
    if not st.session_state[msgs_key]:
        st.markdown("<div style='text-align:center; color: var(--text-secondary); padding-top: 120px;'>Ask for a script, component, or code review 👨‍💻</div>", unsafe_allow_html=True)
    for msg in st.session_state[msgs_key]:
        render_message(msg["role"], msg["content"])

if prompt := st.chat_input("Ask the coding agent anything..."):
    st.session_state[msgs_key].append({"role": "user", "content": prompt})

    with messages_container:
        render_message("user", prompt)
        with st.spinner("Writing code..."):
            resp = generate_code(jwt, prompt, st.session_state[conv_key])

            if resp:
                if "error" in resp:
                    st.error(resp["error"])
                else:
                    if not st.session_state[conv_key]:
                        st.session_state[conv_key] = resp.get("conversation_id")
                        fetch_conversations.clear()

                    st.session_state[msgs_key].append({
                        "role": "assistant",
                        "content": resp.get("text_content"),
                    })

                    if resp.get("code"):
                        st.session_state["current_artifact"] = {
                            "language": resp.get("language"),
                            "code": resp.get("code"),
                            "explanation": resp.get("text_content"),
                        }
                    st.rerun()
            else:
                st.error("Failed to generate code.")

