import streamlit as st


def render_metric_card_icon(icon, value, label, delta=None, bg="rgba(79,125,243,0.15)"):
    delta_html = f"<div style='font-size:12px; color: var(--success); margin-top:6px; font-weight:600;'>{delta}</div>" if delta else ""
    st.markdown(f"""
<div style='background-color: var(--bg-card); padding: 20px; border-radius: var(--radius-card); border: 1px solid var(--border); display:flex; align-items:flex-start; gap:14px;'>
<div style='width:40px; height:40px; border-radius:10px; background:{bg}; display:flex; align-items:center; justify-content:center; font-size:18px; flex-shrink:0;'>{icon}</div>
<div>
<div style='font-size:22px; font-weight:700; color: var(--text-primary); line-height:1.2;'>{value}</div>
<div style='font-size:13px; color: var(--text-secondary); margin-top:2px;'>{label}</div>
{delta_html}
</div>
</div>
    """, unsafe_allow_html=True)


def render_agent_card_nav(name, description, icon, page, bg="rgba(79,125,243,0.15)"):
    st.markdown(f"""
<div class='nova-agent-card'>
<div class='nova-agent-card-icon' style='background:{bg};'>{icon}</div>
<div class='nova-agent-card-name'>{name}</div>
<div class='nova-agent-card-desc'>{description}</div>
</div>
    """, unsafe_allow_html=True)
    if st.button("Open →", key=f"open_{page}", width='stretch'):
        st.switch_page(page)


def render_quick_action(icon, label, page, key):
    if st.button(f"{icon}\n{label}", key=key, width='stretch'):
        st.switch_page(page)


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
    st.markdown("""
<div style='background-color: transparent; padding: 24px; border-radius: var(--radius-card); border: 1px dashed var(--border); cursor: pointer; transition: all 0.2s; height: 100%; display: flex; flex-direction: column; align-items: center; text-align: center; justify-content: center;' class='agent-card-hover'>
<div style='font-size: 32px; margin-bottom: 16px; color: var(--text-secondary);'>+</div>
<div style='font-weight: 600; font-size: 16px; margin-bottom: 8px; color: var(--text-secondary);'>Custom Agent</div>
<div style='font-size: 12px; color: var(--text-secondary);'>Build your own workflow</div>
</div>
    """, unsafe_allow_html=True)
