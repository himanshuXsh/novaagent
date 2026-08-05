import base64
import os

import streamlit as st

_STATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "static")

NAV_ITEMS = [
    {"key": "dashboard", "label": "Dashboard", "icon": "🏠", "page": "pages/dashboard.py"},
    {"key": "chat", "label": "AI Chat", "icon": "💬", "page": "pages/chat.py"},
    {"key": "coding", "label": "Coding Agent", "icon": "💻", "page": "pages/coding.py"},
    {"key": "search", "label": "Search Agent", "icon": "🔍", "page": "pages/search.py"},
    {"key": "rag", "label": "RAG Assistant", "icon": "📚", "page": "pages/rag.py"},
    {"key": "images", "label": "Image Generator", "icon": "🖼️", "page": "pages/images.py"},
    {"key": "settings", "label": "Settings", "icon": "⚙️", "page": "pages/settings.py"},
]


@st.cache_data
def _logo_src():
    path = os.path.join(_STATIC_DIR, "logo-full.png")
    if os.path.exists(path):
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        return f"data:image/png;base64,{b64}"
    return ""


def render_sidebar(active: str, user: dict = None, sessions: list = None,
                    on_new_label: str = None, active_session_id: str = None):
    """Renders the persistent left navigation used on every authenticated page.

    active: key from NAV_ITEMS identifying the current page (for highlighting).
    user: user profile dict (name, email, plan) - optional.
    sessions: optional list of {"id","title","created_at"} conversation-style
        history to show under the active nav item (used on Chat/Coding/Search/RAG).
    on_new_label: if provided, renders a "+ New ..." button above the session list.
    active_session_id: id of the currently selected session, for highlighting.
    """
    logo = _logo_src()

    with st.sidebar:
        st.markdown(f"""
<div class="nova-sidebar-header">
    <img src="{logo}" class="nova-sidebar-logo" />
</div>
        """, unsafe_allow_html=True)

        st.markdown("<div class='nova-nav-list'>", unsafe_allow_html=True)
        for item in NAV_ITEMS:
            is_active = item["key"] == active
            clicked = st.sidebar.button(
                f"{item['icon']}  {item['label']}",
                key=f"nav_{item['key']}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            )
            if clicked and not is_active:
                # Clear target page's conversation state to ensure a fresh workspace on arrival
                target_key = item["key"]
                st.session_state[f"{target_key}_conv_id"] = None
                st.session_state[f"{target_key}_messages"] = []
                if target_key == "coding":
                    st.session_state["current_artifact"] = None
                    
                st.switch_page(item["page"])
        st.markdown("</div>", unsafe_allow_html=True)

        # Contextual session list (isolated per agent workspace)
        if sessions is not None:
            st.markdown("<div class='nova-sidebar-divider'></div>", unsafe_allow_html=True)
            if on_new_label:
                if st.sidebar.button(f"➕ {on_new_label}", key=f"new_session_{active}", use_container_width=True, type="primary"):
                    st.session_state[f"{active}_conv_id"] = None
                    st.session_state[f"{active}_messages"] = []
                    if active == "coding":
                        st.session_state["current_artifact"] = None
                    st.rerun()

            st.markdown("<div class='nova-sidebar-section-title'>Recent</div>", unsafe_allow_html=True)
            if not sessions:
                st.markdown("<div class='nova-sidebar-empty'>No sessions yet</div>", unsafe_allow_html=True)
            for s in sessions[:12]:
                is_sel = s.get("id") == active_session_id
                label = s.get("title") or "Untitled"
                if st.sidebar.button(label, key=f"sess_{active}_{s.get('id')}", use_container_width=True):
                    st.session_state[f"{active}_conv_id"] = s.get("id")
                    st.session_state[f"{active}_messages"] = None  # force reload by caller
                    if active == "coding":
                        st.session_state["current_artifact"] = None
                    st.rerun()

        st.markdown("<div class='nova-sidebar-spacer'></div>", unsafe_allow_html=True)

        if user:
            name = user.get("name") or "User"
            email = user.get("email", "")
            plan = (user.get("plan") or "Free").title()
            initial = name[0].upper() if name else "U"
            st.markdown(f"""
<div class="nova-user-card">
    <div class="nova-user-avatar">{initial}</div>
    <div class="nova-user-meta">
        <div class="nova-user-name">{name}</div>
        <div class="nova-user-email">{email}</div>
    </div>
</div>
<div class="nova-plan-badge">{plan} Plan</div>
            """, unsafe_allow_html=True)

        credits = (user or {}).get("credits")
        if credits is not None:
            st.markdown(f"""
<div class="nova-credits-card">
    <div class="nova-credits-label">Credits Left</div>
    <div class="nova-credits-value">{credits}</div>
    <div class="nova-progress-track"><div class="nova-progress-fill" style="width: 45%;"></div></div>
</div>
            """, unsafe_allow_html=True)

        st.markdown("<div class='nova-version-footer'>v2.0.0 &nbsp;•&nbsp; All systems operational</div>", unsafe_allow_html=True)


def render_topbar(icon: str, title: str, subtitle: str = "", user: dict = None, search_placeholder: str = None):
    """Top bar with page icon/title/subtitle on the left and credits/notifications/avatar on the right."""
    left, right = st.columns([3, 2])

    with left:
        if search_placeholder:
            # We use a container to hold search so results render right below it
            search_query = st.text_input("Search", placeholder=search_placeholder, label_visibility="collapsed", key="dashboard_search")
            if search_query:
                from frontend.utils.api_client import search_dashboard
                jwt = st.session_state.get("jwt", "")
                with st.spinner("Searching..."):
                    results = search_dashboard(jwt, search_query)
                    
                st.markdown("<div style='padding: 10px; border: 1px solid var(--border); border-radius: var(--radius-card); background: rgba(0,0,0,0.2);'>", unsafe_allow_html=True)
                if not results:
                    st.markdown("""
                    <div style='text-align:center; padding: 20px; color: var(--text-secondary);'>
                        <div style='font-size: 30px; margin-bottom: 10px;'>🔍</div>
                        <div>No results found for your query.</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("<div style='font-weight:bold; margin-bottom: 10px;'>Search Results:</div>", unsafe_allow_html=True)
                    for r in results:
                        icon = "💬" if r["type"] == "conversation" else "📄"
                        st.markdown(f"<div style='margin-bottom:5px;'>{icon} <b>{r['title']}</b> <span style='color:var(--text-secondary); font-size:12px;'>({r['agent_type']})</span></div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"""
<div class="nova-topbar-title">
    <div class="nova-topbar-icon">{icon}</div>
    <div>
        <div class="nova-topbar-heading">{title}</div>
        <div class="nova-topbar-subheading">{subtitle}</div>
    </div>
</div>
            """, unsafe_allow_html=True)

    with right:
        credits = (user or {}).get("credits", "—")
        name = (user or {}).get("name") or "User"
        
        st.markdown("""
        <style>
        .topbar-right-container { display: flex; align-items: center; justify-content: flex-end; gap: 16px; margin-top: 5px; }
        .topbar-credit { background: rgba(255,255,255,0.05); padding: 6px 12px; border-radius: 20px; font-size: 13px; border: 1px solid var(--border); }
        .topbar-bell { font-size: 18px; cursor: pointer; }
        </style>
        """, unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns([2, 1, 2])
        with c1:
            st.markdown(f"<div class='topbar-right-container'><div class='topbar-credit'>⚡ {credits} Credits</div></div>", unsafe_allow_html=True)
        with c2:
            st.markdown("<div class='topbar-right-container'><div class='topbar-bell'>🔔</div></div>", unsafe_allow_html=True)
        with c3, st.popover(f"👤 {name}", use_container_width=True):
            if st.button("Profile", use_container_width=True):
                st.switch_page("pages/settings.py")
            if st.button("Account Settings", use_container_width=True):
                st.switch_page("pages/settings.py")
            if st.button("Billing", use_container_width=True):
                st.switch_page("pages/billing.py")
            st.divider()
            if st.button("Logout", type="primary", use_container_width=True):
                st.session_state.clear()
                st.switch_page("pages/login.py")
