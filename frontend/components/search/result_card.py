import re

import streamlit as st


def render_result_card(result_data):
    if not result_data:
        return
        
    answer = result_data.get("answer", "")
    sources = result_data.get("sources", [])
    images = result_data.get("images", [])
    
    # Simple regex to style citations in text
    styled_answer = re.sub(r'\[(\d+)\]', r'<span class="source-badge" style="display:inline-flex; width:18px; height:18px; font-size:10px; margin-left:4px;">\1</span>', answer)
    
    st.markdown(f"""
<div class="search-result-card">
<div style="margin-bottom: 16px; font-size: 16px; line-height: 1.6; color: var(--text-primary);">
{styled_answer}
</div>
    """, unsafe_allow_html=True)
    
    if images:
        st.markdown("<div style='font-weight: 600; margin-top: 24px; margin-bottom: 12px;'>Images</div>", unsafe_allow_html=True)
        cols = st.columns(min(len(images), 4))
        for idx, img in enumerate(images[:4]):
            with cols[idx]:
                st.markdown(f"<img src='{img['thumbnail_url']}' class='search-image' />", unsafe_allow_html=True)
                
    if sources:
        st.markdown("<div class='search-sources'>", unsafe_allow_html=True)
        st.markdown("<div style='font-weight: 600; margin-bottom: 16px;'>Sources</div>", unsafe_allow_html=True)
        
        for src in sources:
            st.markdown(f"""
<div class="source-item">
<div class="source-badge">{src['id']}</div>
<div class="source-details">
<a href="{src['url']}" target="_blank" class="source-title">{src['title']}</a>
<span class="source-url">{src['url'][:60]}...</span>
</div>
</div>
            """, unsafe_allow_html=True)
            
        st.markdown("</div>", unsafe_allow_html=True)
        
    st.markdown("</div>", unsafe_allow_html=True)
