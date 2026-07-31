import streamlit as st
import json
import requests
from sseclient import SSEClient
from frontend.components.chat.sidebar import render_chat_sidebar
from frontend.components.chat.message_renderer import render_message
from frontend.components.layout.navbar import render_navbar
from frontend.utils.api_client import fetch_user_profile, fetch_conversations, fetch_messages

if "jwt" not in st.session_state:
    st.switch_page("app.py")

jwt = st.session_state["jwt"]
user = fetch_user_profile(jwt)

if not user:
    st.session_state.clear()
    st.switch_page("app.py")

if "current_conv_id" not in st.session_state:
    st.session_state["current_conv_id"] = None
    
if "messages" not in st.session_state or st.session_state["messages"] is None:
    if st.session_state["current_conv_id"]:
        st.session_state["messages"] = fetch_messages(jwt, st.session_state["current_conv_id"])
    else:
        st.session_state["messages"] = []

# Fetch sidebar data
conversations = fetch_conversations(jwt)

# Layout
render_chat_sidebar(conversations, st.session_state["current_conv_id"])

st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)
render_navbar(user_info=user)

st.markdown("### Chat Workspace")

# Chat Interface
messages_container = st.container(height=600, border=False)

with messages_container:
    for msg in st.session_state["messages"]:
        render_message(msg["role"], msg["content"])

if prompt := st.chat_input("Message NovaAgent..."):
    # Render user message immediately
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with messages_container:
        render_message("user", prompt)
    
    # Render assistant response via SSE
    with messages_container:
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""
            
            # SSE Request
            url = f"http://localhost:8000/api/v1/chat/message"
            headers = {
                "Authorization": f"Bearer {jwt}",
                "Content-Type": "application/json"
            }
            data = {
                "content": prompt,
                "agent_type": "chat"
            }
            if st.session_state["current_conv_id"]:
                data["conversation_id"] = st.session_state["current_conv_id"]
                
            response = requests.post(url, headers=headers, json=data, stream=True)
            
            if response.status_code == 200:
                client = SSEClient(response)
                for event in client.events():
                    if event.event == "message":
                        try:
                            chunk_data = json.loads(event.data)
                            full_response += chunk_data.get("content", "")
                            response_placeholder.markdown(full_response + "▌")
                        except:
                            pass
                    elif event.event == "done":
                        try:
                            end_data = json.loads(event.data)
                            if not st.session_state["current_conv_id"]:
                                st.session_state["current_conv_id"] = end_data.get("conversation_id")
                        except:
                            pass
                
                response_placeholder.markdown(full_response)
                st.session_state["messages"].append({"role": "assistant", "content": full_response})
            else:
                st.error(f"Error: {response.text}")
                
    st.rerun()
