import streamlit as st

def render_metric_card(title, value, delta=None, delta_color="success"):
    delta_html = ""
    if delta:
        color = "var(--success)" if delta_color == "success" else "var(--danger)"
        delta_html = f"<div style='font-size: 12px; color: {color}; margin-top: 4px;'>{delta}</div>"
        
    st.markdown(f"""
        <div style='background-color: var(--bg-card); padding: 24px; border-radius: var(--radius-card); border: 1px solid var(--border); box-shadow: 0 4px 24px rgba(0,0,0,0.25); display: flex; flex-direction: column;'>
            <div style='color: var(--text-secondary); font-size: 14px; font-weight: 600; margin-bottom: 8px;'>{title}</div>
            <div style='color: var(--text-primary); font-size: 32px; font-weight: 700;'>{value}</div>
            {delta_html}
        </div>
    """, unsafe_allow_html=True)

def render_agent_card(name, description, icon):
    st.markdown(f"""
        <div style='background-color: var(--bg-secondary); padding: 24px; border-radius: var(--radius-card); border: 1px solid var(--border); cursor: pointer; transition: all 0.2s; height: 100%; display: flex; flex-direction: column; align-items: center; text-align: center; justify-content: center;' class='agent-card-hover'>
            <div style='font-size: 32px; margin-bottom: 16px;'>{icon}</div>
            <div style='font-weight: 600; font-size: 16px; margin-bottom: 8px;'>{name}</div>
            <div style='font-size: 12px; color: var(--text-secondary);'>{description}</div>
        </div>
    """, unsafe_allow_html=True)
    
def render_add_custom_agent_card():
    st.markdown(f"""
        <div style='background-color: transparent; padding: 24px; border-radius: var(--radius-card); border: 1px dashed var(--border); cursor: pointer; transition: all 0.2s; height: 100%; display: flex; flex-direction: column; align-items: center; text-align: center; justify-content: center;' class='agent-card-hover'>
            <div style='font-size: 32px; margin-bottom: 16px; color: var(--text-secondary);'>+</div>
            <div style='font-weight: 600; font-size: 16px; margin-bottom: 8px; color: var(--text-secondary);'>Custom Agent</div>
            <div style='font-size: 12px; color: var(--text-secondary);'>Build your own workflow</div>
        </div>
    """, unsafe_allow_html=True)
