import streamlit as st

def render_artifact_panel(artifact):
    if not artifact:
        st.markdown("""
            <div class='artifact-panel' style='display: flex; flex-direction: column; justify-content: center; align-items: center; color: var(--text-secondary); text-align: center;'>
                <div style='font-size: 48px; margin-bottom: 16px;'>💻</div>
                <div style='font-weight: 600; margin-bottom: 8px;'>No Code Artifacts Yet</div>
                <div style='font-size: 14px;'>Ask the Coding Agent to generate a script, function, or snippet!</div>
            </div>
        """, unsafe_allow_html=True)
        return
        
    language = artifact.get("language", "text")
    code = artifact.get("code", "")
    
    st.markdown(f"""
        <div class='artifact-panel'>
            <div class='artifact-header'>
                <div class='artifact-title'>
                    <span>✨</span>
                    Generated Code
                </div>
                <div class='artifact-language-badge'>{language.upper()}</div>
            </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Code", "Preview"])
    
    with tab1:
        st.code(code, language=language)
        
    with tab2:
        if language.lower() in ["html", "html5"]:
            st.components.v1.html(code, height=500, scrolling=True)
        else:
            st.info("Preview only available for HTML outputs.")
            
    st.markdown("</div>", unsafe_allow_html=True)
