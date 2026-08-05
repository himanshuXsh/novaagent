import streamlit as st

# Languages that get a live rendered Preview tab.
PREVIEW_LANGUAGES = {"html", "html5", "css", "javascript", "js", "jsx", "react", "tsx", "typescript"}
# Everything else (python, sql, shell/bash, markdown, etc.) only ever shows
# Code / Copy / Download / Explanation - never a Preview tab.


def _build_preview_doc(language: str, code: str) -> str:
    lang = language.lower()
    if lang in ("html", "html5"):
        return code
    if lang == "css":
        return f"<html><body style='background:#fff;padding:16px;'><style>{code}</style><div>Preview uses placeholder markup - inspect your CSS rules against it.</div></body></html>"
    return f"""
<html>
<body style="background:#0B0F19;color:#F8FAFC;font-family:Inter,sans-serif;padding:16px;">
<div id="root"></div>
<script>
try {{
{code}
}} catch (e) {{
  document.body.innerHTML = '<pre style="color:#EF4444;">' + e + '</pre>';
}}
</script>
</body>
</html>
"""


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

    language = (artifact.get("language") or "text").lower()
    code = artifact.get("code", "")
    explanation = artifact.get("explanation", "")
    show_preview = language in PREVIEW_LANGUAGES

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

    tab_labels = ["Code", "Preview", "Explanation"] if show_preview else ["Code", "Explanation"]
    tabs = st.tabs(tab_labels)

    with tabs[0]:
        st.code(code, language=language if language != "html5" else "html")
        st.download_button("⬇ Download", data=code, file_name=f"snippet.{_extension(language)}", width='stretch')

    if show_preview:
        with tabs[1]:
            st.components.v1.html(_build_preview_doc(language, code), height=500, scrolling=True)
        with tabs[2]:
            st.markdown(explanation or "_No explanation provided for this snippet yet._")
    else:
        with tabs[1]:
            st.markdown(explanation or "_No explanation provided for this snippet yet._")

    st.markdown("</div>", unsafe_allow_html=True)


def _extension(language):
    return {
        "python": "py", "sql": "sql", "shell": "sh", "bash": "sh", "markdown": "md",
        "html": "html", "html5": "html", "css": "css", "javascript": "js", "js": "js",
        "jsx": "jsx", "react": "jsx", "tsx": "tsx", "typescript": "ts",
    }.get(language, "txt")
