import streamlit as st

def render_message(role, content):
    with st.chat_message(role):
        st.markdown(content)
