import json

import requests
import streamlit as st

st.set_page_config(layout="wide", initial_sidebar_state="expanded")
from sseclient import SSEClient

from frontend.components.chat.message_renderer import render_message
from frontend.components.layout.shell import render_sidebar, render_topbar
from frontend.utils.api_client import (
    API_BASE_URL,
    fetch_balance,
    fetch_conversations,
    fetch_messages,
    fetch_user_profile,
)
from frontend.utils.css_loader import load_all_css

load_all_css()

AGENT_KEY = "chat"

if "jwt" not in st.session_state:
    st.switch_page("app.py")

jwt = st.session_state["jwt"]
user = fetch_user_profile(jwt)

if not user:
    st.session_state.clear()
    st.switch_page("app.py")

balance = fetch_balance(jwt) or {}
user_for_shell = {**user, "credits": balance.get("credits")}

# --- Isolated per-agent session state -------------------------------------
# Every agent workspace (chat / coding / search / rag) keeps its own
# conversation id + message list under a namespaced key so switching agents
# never leaks another agent's messages into view.
conv_key = f"{AGENT_KEY}_conv_id"
msgs_key = f"{AGENT_KEY}_messages"

if conv_key not in st.session_state:
    st.session_state[conv_key] = None

if msgs_key not in st.session_state or st.session_state[msgs_key] is None:
    if st.session_state[conv_key]:
        st.session_state[msgs_key] = fetch_messages(jwt, st.session_state[conv_key])
    else:
        st.session_state[msgs_key] = []

# Only this agent's own history - never mixed with coding/search/rag sessions
all_convs = fetch_conversations(jwt) or []
chat_convs = [c for c in all_convs if c.get("agent_type") == "chat"]

render_sidebar(
    active=AGENT_KEY, user=user_for_shell, sessions=chat_convs,
    on_new_label="New Chat", active_session_id=st.session_state[conv_key],
)

render_topbar(icon="💬", title="AI Chat Agent", subtitle="Your general-purpose AI assistant", user=user_for_shell)
st.markdown("<div class='nova-page-header-spacer'></div>", unsafe_allow_html=True)

messages_container = st.container(height=560, border=False)

with messages_container:
    if not st.session_state[msgs_key]:
        st.markdown("<div style='text-align:center; color: var(--text-secondary); padding-top: 120px;'>Start a new conversation below 👋</div>", unsafe_allow_html=True)
    for msg in st.session_state[msgs_key]:
        render_message(msg["role"], msg["content"])

if prompt := st.chat_input("Message NovaAgent..."):
    st.session_state[msgs_key].append({"role": "user", "content": prompt})
    with messages_container:
        render_message("user", prompt)

        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""

            url = f"{API_BASE_URL}/chat/message"
            headers = {"Authorization": f"Bearer {jwt}", "Content-Type": "application/json"}
            data = {"content": prompt, "agent_type": "chat"}
            if st.session_state[conv_key]:
                data["conversation_id"] = st.session_state[conv_key]

            try:
                response = requests.post(url, headers=headers, json=data, stream=True, timeout=30)

                if response.status_code == 200:
                    client = SSEClient(response)
                    for event in client.events():
                        if event.event == "message":
                            try:
                                chunk_data = json.loads(event.data)
                                full_response += chunk_data.get("content", "")
                                response_placeholder.markdown(full_response + "▌")
                            except Exception:
                                pass
                        elif event.event == "done":
                            try:
                                end_data = json.loads(event.data)
                                if not st.session_state[conv_key]:
                                    st.session_state[conv_key] = end_data.get("conversation_id")
                                    fetch_conversations.clear()
                            except Exception:
                                pass

                    response_placeholder.markdown(full_response)
                    st.session_state[msgs_key].append({"role": "assistant", "content": full_response})
                elif response.status_code == 402:
                    st.error("Insufficient credits to perform this action.")
                    st.stop()
                else:
                    st.error(f"Error ({response.status_code}): {response.text}")
                    st.stop()
            except requests.exceptions.Timeout:
                st.error("The request timed out. Please try again.")
                st.stop()
            except Exception as e:
                st.error(f"Error: {e!s}")
                import traceback
                st.error(traceback.format_exc())
                st.stop()

    st.rerun()
