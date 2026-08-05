
import streamlit as st

st.set_page_config(layout="wide", initial_sidebar_state="expanded")

from frontend.components.cards import render_agent_card_nav, render_metric_card_icon
from frontend.components.charts import render_usage_chart
from frontend.components.layout.shell import render_sidebar, render_topbar
from frontend.utils.api_client import (
    fetch_balance,
    fetch_dashboard_activity,
    fetch_dashboard_charts,
    fetch_dashboard_metrics,
    fetch_user_profile,
)
from frontend.utils.css_loader import load_all_css

load_all_css()

if "jwt" not in st.session_state:
    st.switch_page("app.py")

jwt = st.session_state["jwt"]


@st.cache_data(ttl=60)
def load_core_metrics(token):
    return (
        fetch_user_profile(token),
        fetch_dashboard_metrics(token),
        fetch_balance(token),
    )

@st.cache_data(ttl=60)
def load_charts_data(token):
    return fetch_dashboard_charts(token)

@st.cache_data(ttl=60)
def load_activity_data(token):
    return fetch_dashboard_activity(token)

user, metrics, balance = load_core_metrics(jwt)

if not user:
    st.session_state.clear()
    st.switch_page("app.py")

credits = (balance or {}).get("credits", metrics.get("credits", 0))
user_for_shell = {**user, "credits": credits}

render_sidebar(active="dashboard", user=user_for_shell)
render_topbar(icon="🏠", title="Dashboard", subtitle="", user=user_for_shell,
              search_placeholder="Search anything...")

st.markdown("<div class='nova-page-header-spacer'></div>", unsafe_allow_html=True)

name = (user.get("name") or "there").split(" ")[0]
st.markdown(f"""
<div class="nova-welcome-banner">
  <div class="nova-welcome-greeting">Good to see you, <span class="accent">{name}</span> 👋</div>
  <div class="nova-welcome-sub">Welcome back to your AI workspace.</div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    render_metric_card_icon("⚡", credits, "Credits Left", bg="rgba(79,125,243,0.15)")
with col2:
    render_metric_card_icon("💬", metrics.get("conversations", 0), "Conversations", bg="rgba(109,94,247,0.15)")
with col3:
    render_metric_card_icon("📨", metrics.get("messages", 0), "Messages Sent", bg="rgba(34,197,94,0.15)")
with col4:
    render_metric_card_icon("📁", metrics.get("files", 0), "Files Processed", bg="rgba(245,158,11,0.15)")

st.markdown("<div class='dashboard-section-title'>Choose an Agent</div>", unsafe_allow_html=True)

agents = [
    ("AI Chat", "Smart conversations with AI", "💬", "pages/chat.py", "rgba(79,125,243,0.15)"),
    ("Coding Agent", "Write, debug & optimize code", "💻", "pages/coding.py", "rgba(34,197,94,0.15)"),
    ("Search Agent", "Search the web & get real-time insights", "🔍", "pages/search.py", "rgba(109,94,247,0.15)"),
    ("RAG Assistant", "Chat with your documents", "📚", "pages/rag.py", "rgba(245,158,11,0.15)"),
    ("Image Generator", "Create stunning images with AI", "🖼️", "pages/images.py", "rgba(236,72,153,0.15)"),
]

cols = st.columns(3)
for i, (name_a, desc, icon, page, bg) in enumerate(agents):
    with cols[i % 3]:
        render_agent_card_nav(name_a, desc, icon, page, bg)

st.markdown("<div class='dashboard-section-title'>Analytics & Activity</div>", unsafe_allow_html=True)

chart_col, activity_col = st.columns([2, 1])

with chart_col:
    st.markdown("<div class='nova-panel'>", unsafe_allow_html=True)
    st.markdown("<div class='nova-panel-title'>Credits Usage</div>", unsafe_allow_html=True)
    with st.spinner("Loading charts..."):
        charts = load_charts_data(jwt)
        render_usage_chart((charts or {}).get("usage"))
    st.markdown("</div>", unsafe_allow_html=True)

with activity_col:
    st.markdown("<div class='nova-panel' style='height:100%;'>", unsafe_allow_html=True)
    st.markdown("<div class='nova-panel-title'>Recent Activity</div>", unsafe_allow_html=True)
    with st.spinner("Loading activity..."):
        activity = load_activity_data(jwt)
        if not activity:
            st.markdown("<div style='color: var(--text-secondary); font-size: 13px;'>No recent activity yet.</div>", unsafe_allow_html=True)
        else:
            for item in activity:
                st.markdown(f"""
    <div class='activity-item'>
    <div>
    <div class='activity-title'>{item.get('title')}</div>
    <div class='activity-meta'>Agent: {item.get('agent_type')}</div>
    </div>
    <div class='activity-meta'>{(item.get('created_at') or '')[:10]}</div>
    </div>
                """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


