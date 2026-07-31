import streamlit as st
import os
import tempfile
from frontend.components.layout.navbar import render_navbar
from frontend.utils.api_client import fetch_user_profile, upload_rag_document, query_rag_document, fetch_rag_documents

if "jwt" not in st.session_state:
    st.switch_page("app.py")

jwt = st.session_state["jwt"]
user = fetch_user_profile(jwt)

if not user:
    st.session_state.clear()
    st.switch_page("app.py")

st.sidebar.markdown("""
    <div style='text-align: center; margin-bottom: 32px;'>
        <img src='app/static/logo.png' width='50' style='margin-bottom: 8px;' />
        <div style='font-weight: 700; font-size: 20px;'>NovaAgent</div>
    </div>
""", unsafe_allow_html=True)

st.sidebar.page_link("app.py", label="Back to Dashboard", icon="🔙")

render_navbar(user_info=user)

st.markdown("<h2 style='text-align: center; margin-top: 16px;'>RAG Document Agent</h2>", unsafe_allow_html=True)

if "active_rag_doc" not in st.session_state:
    st.session_state["active_rag_doc"] = None

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### 1. Upload PDF")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    if uploaded_file is not None:
        if st.button("Process Document", type="primary"):
            with st.spinner("Extracting & Embedding..."):
                # Save to temp
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded_file.getvalue())
                    tmp_path = tmp.name
                    
                res = upload_rag_document(jwt, tmp_path, uploaded_file.name)
                os.unlink(tmp_path)
                
                if res:
                    st.success("Document processed!")
                    st.session_state["active_rag_doc"] = res
                else:
                    st.error("Upload failed.")
                    
    st.markdown("### Your Documents")
    docs = fetch_rag_documents(jwt)
    if not docs:
        st.info("No documents uploaded.")
    else:
        for d in docs:
            st.markdown(f"""
            <div class="rag-doc-item">
                <span>{d['filename']}</span>
            </div>
            """, unsafe_allow_html=True)

with col2:
    st.markdown("### 2. Query Document")
    if not st.session_state.get("active_rag_doc"):
        st.info("Upload and process a document first to start querying.")
    else:
        doc = st.session_state["active_rag_doc"]
        st.markdown(f"**Active Document:** {doc['filename']}")
        
        query = st.text_input("Ask a question about the document:")
        if st.button("Ask"):
            if query:
                with st.spinner("Searching and synthesizing..."):
                    res = query_rag_document(jwt, doc["document_id"], query)
                    if res:
                        st.markdown(f"""
                        <div style='background-color: var(--bg-card); padding: 16px; border-radius: 8px; border: 1px solid var(--border); margin-top: 16px;'>
                            <strong>Q: {query}</strong><br><br>
                            {res['answer']}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error("Failed to query document.")
            else:
                st.warning("Please enter a question.")
