import streamlit as st

def render_navbar(user_info=None):
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.markdown("""
            <div style='display: flex; align-items: center; padding: 8px 16px; background-color: var(--bg-secondary); border-radius: var(--radius-button); border: 1px solid var(--border); width: 300px;'>
                <span style='color: var(--text-secondary); margin-right: 8px;'>🔍</span>
                <span style='color: var(--text-secondary); font-size: 14px;'>Search... (⌘K)</span>
            </div>
        """, unsafe_allow_html=True)
        
    with col2:
        if user_info:
            name = user_info.get("name", "User")
            plan = user_info.get("plan", "PRO").upper()
            st.markdown(f"""
                <div style='display: flex; justify-content: flex-end; align-items: center; height: 100%; gap: 16px;'>
                    <span style='font-size: 20px; cursor: pointer;'>🔔</span>
                    <div style='display: flex; align-items: center; gap: 8px;'>
                        <div style='width: 32px; height: 32px; background: var(--accent-gradient); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold;'>
                            {name[0].upper()}
                        </div>
                        <div style='display: flex; flex-direction: column; line-height: 1.2;'>
                            <span style='font-size: 14px; font-weight: 600;'>{name}</span>
                            <span style='font-size: 10px; color: var(--accent-primary); font-weight: 700;'>{plan} PLAN</span>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
