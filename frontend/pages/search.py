import streamlit as st
from frontend.components.layout.navbar import render_navbar
from frontend.components.search.result_card import render_result_card
from frontend.utils.api_client import fetch_user_profile, perform_search

if "jwt" not in st.session_state:
    st.switch_page("app.py")

jwt = st.session_state["jwt"]
user = fetch_user_profile(jwt)

if not user:
    st.session_state.clear()
    st.switch_page("app.py")

# Simple Sidebar for Search
st.sidebar.markdown("""
    <div style='text-align: center; margin-bottom: 32px;'>
        <img src='app/static/logo.png' width='50' style='margin-bottom: 8px;' />
        <div style='font-weight: 700; font-size: 20px;'>NovaAgent</div>
    </div>
""", unsafe_allow_html=True)

st.sidebar.page_link("app.py", label="Back to Dashboard", icon="🔙")

# Navbar
render_navbar(user_info=user)

st.markdown("<div class='search-container'>", unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center; margin-bottom: 32px;'>Search the Web</h2>", unsafe_allow_html=True)

# Search Input
query = st.chat_input("Ask anything (e.g. 'Latest news in AI')")

if "search_result" not in st.session_state:
    st.session_state["search_result"] = None

if query:
    with st.spinner("Searching and synthesizing..."):
        result = perform_search(jwt, query)
        if result:
            st.session_state["search_result"] = result
        else:
            st.error("Failed to perform search.")

if st.session_state["search_result"]:
    render_result_card(st.session_state["search_result"])

st.markdown("</div>", unsafe_allow_html=True)
