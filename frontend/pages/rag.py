import os
import tempfile

import streamlit as st

st.set_page_config(layout="wide", initial_sidebar_state="expanded")

from frontend.components.layout.shell import render_sidebar, render_topbar
from frontend.utils.api_client import (
    fetch_balance,
    fetch_rag_documents,
    fetch_user_profile,
    query_rag_document,
    upload_rag_document,
)
from frontend.utils.css_loader import load_all_css

load_all_css()

AGENT_KEY = "rag"

if "jwt" not in st.session_state:
    st.switch_page("app.py")

jwt = st.session_state["jwt"]
user = fetch_user_profile(jwt)

if not user:
    st.session_state.clear()
    st.switch_page("app.py")

balance = fetch_balance(jwt) or {}
user_for_shell = {**user, "credits": balance.get("credits")}

render_sidebar(active=AGENT_KEY, user=user_for_shell)
render_topbar(icon="📚", title="RAG Assistant", subtitle="Upload, manage and chat with your documents", user=user_for_shell)
st.markdown("<div class='nova-page-header-spacer'></div>", unsafe_allow_html=True)

if "active_rag_doc" not in st.session_state:
    st.session_state["active_rag_doc"] = None
if "rag_answers" not in st.session_state:
    st.session_state["rag_answers"] = []

col1, col2 = st.columns([1, 1.4])

with col1:
    st.markdown("<div class='nova-panel'>", unsafe_allow_html=True)
    st.markdown("<div class='nova-panel-title'>📤 Upload a document</div>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Drag & drop or browse", type="pdf", label_visibility="collapsed")
    if uploaded_file is not None:
        if st.button("Process Document", type="primary", use_container_width=True):
            with st.spinner("Extracting & embedding..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded_file.getvalue())
                    tmp_path = tmp.name

                res = upload_rag_document(jwt, tmp_path, uploaded_file.name)
                os.unlink(tmp_path)

                if res and "error" in res:
                    st.error(res["error"])
                elif res:
                    st.success("Document processed!")
                    fetch_rag_documents.clear()
                    st.session_state["active_rag_doc"] = res
                else:
                    st.error("Upload failed due to an unknown error.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='nova-panel' style='margin-top:16px;'>", unsafe_allow_html=True)
    st.markdown("<div class='nova-panel-title'>Your Documents</div>", unsafe_allow_html=True)
    docs = fetch_rag_documents(jwt) or []
    if not docs:
        st.markdown("<div style='color: var(--text-secondary); font-size: 13px;'>No documents uploaded yet.</div>", unsafe_allow_html=True)
    else:
        for d in docs:
            is_active = st.session_state.get("active_rag_doc") and st.session_state["active_rag_doc"].get("document_id") == d.get("document_id")
            st.markdown(f"""
<div class="rag-doc-item" style="{'border-color: var(--accent-primary);' if is_active else ''}">
<span>📄 {d.get('filename')}</span>
</div>
            """, unsafe_allow_html=True)
            if not is_active:
                if st.button("Use this document", key=f"use_{d.get('document_id')}", use_container_width=True):
                    st.session_state["active_rag_doc"] = d
                    st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='nova-panel'>", unsafe_allow_html=True)
    st.markdown("<div class='nova-panel-title'>Ask your documents</div>", unsafe_allow_html=True)

    if not st.session_state.get("active_rag_doc"):
        st.markdown("<div style='color: var(--text-secondary); font-size: 13px;'>Upload and process a document first, or select one on the left, to start asking questions.</div>", unsafe_allow_html=True)
    else:
        doc = st.session_state["active_rag_doc"]
        st.markdown(f"<div style='font-size:13px; color: var(--text-secondary); margin-bottom:12px;'>Active document: <strong style='color: var(--text-primary);'>{doc.get('filename')}</strong></div>", unsafe_allow_html=True)

        query = st.chat_input("Ask anything about your documents...")
        if query:
            with st.spinner("Searching and synthesizing..."):
                res = query_rag_document(jwt, doc["document_id"], query)
                if res and "error" in res:
                    st.error(res["error"])
                elif res:
                    st.session_state["rag_answers"].insert(0, {"q": query, "a": res.get("answer")})
                else:
                    st.error("Failed to query document due to an unknown error.")

        for item in st.session_state["rag_answers"]:
            st.markdown(f"""
<div style='background-color: var(--bg-secondary); padding: 16px; border-radius: var(--radius-button); border: 1px solid var(--border); margin-bottom: 12px;'>
<strong>Q: {item['q']}</strong><br><br>
{item['a']}
</div>
            """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
