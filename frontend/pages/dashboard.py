import streamlit as st
from frontend.components.layout.sidebar import render_sidebar
from frontend.components.layout.navbar import render_navbar
from frontend.components.cards import render_metric_card, render_agent_card, render_add_custom_agent_card
from frontend.components.charts import render_usage_chart, render_distribution_chart
from frontend.utils.api_client import fetch_user_profile, fetch_dashboard_metrics, fetch_dashboard_charts, fetch_dashboard_activity

# Ensure JWT is in session
if "jwt" not in st.session_state:
    st.switch_page("app.py")

jwt = st.session_state["jwt"]

# Fetch data
@st.cache_data(ttl=60)
def load_dashboard_data(token):
    user = fetch_user_profile(token)
    metrics = fetch_dashboard_metrics(token)
    charts = fetch_dashboard_charts(token)
    activity = fetch_dashboard_activity(token)
    return user, metrics, charts, activity

user, metrics, charts, activity = load_dashboard_data(jwt)

if not user:
    st.session_state.clear()
    st.switch_page("app.py")

# Render Layout
render_sidebar()
render_navbar(user_info=user)

st.markdown("<div class='dashboard-section-title'>Overview</div>", unsafe_allow_html=True)

# Metrics Row
col1, col2, col3, col4 = st.columns(4)
with col1:
    render_metric_card("Credits Balance", metrics.get("credits", 0))
with col2:
    render_metric_card("Conversations", metrics.get("conversations", 0))
with col3:
    render_metric_card("Messages Generated", metrics.get("messages", 0))
with col4:
    render_metric_card("Files Generated", metrics.get("files", 0))

st.markdown("<div class='dashboard-section-title'>Agents Workspace</div>", unsafe_allow_html=True)

# Agents Grid
row1_col1, row1_col2, row1_col3 = st.columns(3)
with row1_col1:
    render_agent_card("Chat Agent", "General AI assistant", "💬")
with row1_col2:
    render_agent_card("Coding Agent", "Write and review code", "💻")
with row1_col3:
    render_agent_card("Search Agent", "Web search with citations", "🔍")

st.markdown("<br>", unsafe_allow_html=True)

row2_col1, row2_col2, row2_col3 = st.columns(3)
with row2_col1:
    render_agent_card("Document RAG", "Chat with your files", "📄")
with row2_col2:
    render_agent_card("Image Gen", "Create unique visuals", "🎨")
with row2_col3:
    render_add_custom_agent_card()

st.markdown("<div class='dashboard-section-title'>Analytics & Activity</div>", unsafe_allow_html=True)

chart_col, activity_col = st.columns([2, 1])

with chart_col:
    st.markdown("<div style='background-color: var(--bg-card); border-radius: var(--radius-card); padding: 16px; border: 1px solid var(--border);'>", unsafe_allow_html=True)
    render_usage_chart(charts.get("usage"))
    st.markdown("</div>", unsafe_allow_html=True)
    
with activity_col:
    st.markdown("""
        <div style='background-color: var(--bg-card); border-radius: var(--radius-card); padding: 24px; border: 1px solid var(--border); height: 100%;'>
            <div style='font-weight: 600; margin-bottom: 16px; color: var(--text-primary);'>Recent Activity</div>
    """, unsafe_allow_html=True)
    
    if not activity:
        st.info("No recent activity.")
    else:
        for item in activity:
            st.markdown(f"""
                <div class='activity-item'>
                    <div>
                        <div class='activity-title'>{item.get('title')}</div>
                        <div class='activity-meta'>Agent: {item.get('agent_type')}</div>
                    </div>
                    <div class='activity-meta'>{item.get('created_at')[:10]}</div>
                </div>
            """, unsafe_allow_html=True)
            
    st.markdown("</div>", unsafe_allow_html=True)
