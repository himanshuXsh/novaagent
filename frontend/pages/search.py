import streamlit as st

st.set_page_config(layout="wide", initial_sidebar_state="expanded")

from frontend.components.layout.shell import render_sidebar, render_topbar
from frontend.components.search.result_card import render_result_card
from frontend.utils.api_client import fetch_balance, fetch_conversations, fetch_messages, fetch_user_profile
from frontend.utils.css_loader import load_all_css
import requests
import json
from sseclient import SSEClient
import os

load_all_css()


def render_search():

    if "jwt" not in st.session_state:
        st.switch_page("app.py")

    jwt = st.session_state["jwt"]
    user = fetch_user_profile(jwt)

    if not user:
        st.session_state.clear()
        st.switch_page("app.py")


    
    balance = fetch_balance(jwt) or {}
    user_for_shell = {**user, "credits": balance.get("credits")}

    conversations = fetch_conversations(jwt, agent_type="search")
    
    if "search_conv_id" not in st.session_state:
        st.session_state["search_conv_id"] = None
        
    if "search_result" not in st.session_state:
        st.session_state["search_result"] = None

    if st.session_state["search_conv_id"] and not st.session_state["search_result"]:
        msgs = fetch_messages(jwt, st.session_state["search_conv_id"])
        assistant_msg = next((m for m in reversed(msgs) if m["role"] == "assistant"), None)
        if assistant_msg:
            try:
                data = json.loads(assistant_msg["content"])
                st.session_state["search_result"] = data
            except:
                pass

    render_sidebar(active="search", user=user_for_shell, sessions=conversations, on_new_label="New Search", active_session_id=st.session_state["search_conv_id"])
    render_topbar(icon="🔍", title="Search Agent", subtitle="Real-time web search with AI insights", user=user_for_shell)
    st.markdown("<div class='nova-page-header-spacer'></div>", unsafe_allow_html=True)

    st.markdown("<div class='search-container'>", unsafe_allow_html=True)

    # Search Input
    query = st.chat_input("Ask anything (e.g. 'Latest news in AI')")


    if query:
        st.session_state["search_result"] = {"sources": [], "images": [], "answer": ""}
        with st.spinner("Searching and synthesizing..."):
            # API_BASE_URL resolves to http://backend:8000/api/v1 inside Docker (server-side Python call)
            API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000/api/v1")
            url = f"{API_BASE_URL}/agents/search"
            headers = {"Authorization": f"Bearer {jwt}", "Content-Type": "application/json"}
            
            try:
                response = requests.post(url, headers=headers, json={"query": query}, stream=True, timeout=30)
                if response.status_code == 200:
                    client = SSEClient(response)
                    
                    # We create placeholders for streaming
                    st.markdown("### Sources")
                    sources_placeholder = st.empty()
                    st.markdown("### Answer")
                    answer_placeholder = st.empty()
                    
                    full_answer = ""
                    for event in client.events():
                        if event.event == "metadata":
                            try:
                                data = json.loads(event.data)
                                st.session_state["search_result"]["sources"] = data.get("sources", [])
                                st.session_state["search_result"]["images"] = data.get("images", [])
                                sources_placeholder.write([s["title"] for s in st.session_state["search_result"]["sources"]])
                            except Exception:
                                pass
                        elif event.event == "message":
                            try:
                                data = json.loads(event.data)
                                full_answer += data.get("content", "")
                                answer_placeholder.markdown(full_answer + "▌")
                            except Exception:
                                pass
                        elif event.event == "done":
                            answer_placeholder.markdown(full_answer)
                            st.session_state["search_result"]["answer"] = full_answer
                            break
                            
                    st.rerun() # Refresh to show the result_card instead
                else:
                    st.error(f"Search failed: {response.status_code}")
            except Exception as e:
                st.error(f"Search failed: {e!s}")

    if st.session_state["search_result"]:
        render_result_card(st.session_state["search_result"])

    st.markdown("</div>", unsafe_allow_html=True)


render_search()
