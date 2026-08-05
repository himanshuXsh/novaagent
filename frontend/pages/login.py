import base64
import os

import streamlit as st

from frontend.utils.api_client import get_dev_login_url, get_google_login_url
from frontend.utils.css_loader import load_all_css
from dotenv import load_dotenv

load_dotenv()
load_all_css()

st.set_page_config(page_title="NovaAgent - Sign in", page_icon="🤖", layout="wide")

# This dummy sidebar element prevents Streamlit from completely destroying the sidebar
# if showSidebarNavigation = false is set in config.toml.
with st.sidebar:
    st.empty()

# Force full screen bleed by removing Streamlit's default container padding
st.markdown("""
<div id="login-page-marker"></div>
<style>
html, body, .stApp {
    overflow: hidden !important;
    height: 100vh !important;
    margin: 0 !important;
    padding: 0 !important;
}
.block-container {
    padding-top: 0rem !important;
    padding-bottom: 0rem !important;
    padding-left: 0rem !important;
    padding-right: 0rem !important;
    max-width: 100% !important;
}
div[data-testid="stSidebarNav"] { display: none !important; }
</style>
""", unsafe_allow_html=True)


# If already logged in, skip straight to the app
if "jwt" in st.session_state:
    st.switch_page("pages/dashboard.py")


def _b64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""


_static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
logo_full_b64 = _b64(os.path.join(_static_dir, "logo-full.png"))
logo_icon_b64 = _b64(os.path.join(_static_dir, "logo-icon.png"))
logo_full_src = f"data:image/png;base64,{logo_full_b64}" if logo_full_b64 else ""
logo_icon_src = f"data:image/png;base64,{logo_icon_b64}" if logo_icon_b64 else ""

FEATURES = [
    ("💬", "AI Chat", "Smart conversations\nthat understand you", "rgba(79,125,243,0.15)"),
    ("💻", "Coding Assistant", "Write, debug & optimize\ncode faster", "rgba(34,197,94,0.15)"),
    ("🔍", "Search Agent", "Real-time web search\nwith insights", "rgba(79,125,243,0.15)"),
    ("🖼️", "Image Generator", "Create stunning images\nwith AI", "rgba(109,94,247,0.15)"),
    ("🛡️", "Secure & Private", "Enterprise-grade security\nfor your data", "rgba(16,185,129,0.15)"),
]

feature_cards_html = "".join([
    f"""<div class="login-feature-card">
<div class="login-feature-icon" style="background:{bg};">{icon}</div>
<div><div class="login-feature-title">{title}</div><div class="login-feature-desc">{desc.replace(chr(10), '<br>')}</div></div>
</div>""" for icon, title, desc, bg in FEATURES
])

login_url = get_google_login_url()

# ------------------------------------------------------------------
# SECURITY: Dev Login (Bypass) must NEVER render in production.
# Matches the reference design, which has no bypass button visible.
# Defaults to "production" (safe default) if ENVIRONMENT isn't set.
# ------------------------------------------------------------------
IS_DEV_ENV = os.getenv("ENVIRONMENT", "production").lower() == "development"
dev_login_url = get_dev_login_url() if IS_DEV_ENV else None
show_dev_login = IS_DEV_ENV and bool(dev_login_url)

dev_login_html = ""
if show_dev_login:
    dev_login_html = f"""
<a href="{dev_login_url}" target="_self" style="text-decoration:none; display:block; margin-bottom: 24px;">
<button class="btn-google btn-dev">
<span style="margin-right: 8px;">🛠️</span> Dev Login (Bypass)
</button>
</a>
"""

st.markdown(f"""
<div class="login-split">
<div class="login-left">
<div>
<img src="{logo_full_src}" class="login-left-logo" />
<div class="login-brand-title">Your Intelligent<br>Multi-Agent <span class="accent">AI Workspace</span></div>
<div class="login-brand-subtitle">All your AI agents. All your tools. One workspace.<br>Built to boost your productivity.</div>
</div>
<img src="{logo_icon_src}" class="login-hero-orb" />
<div class="login-feature-grid">
{feature_cards_html}
</div>
<div class="login-left-footer">© 2025 NovaAgent. All rights reserved.</div>
</div>

<div class="login-right">
<div class="theme-toggle">
<div class="theme-toggle-inner">
<span style="font-size:12px;">🌙</span>
<span style="font-size:12px;opacity:0.5;">☀️</span>
</div>
</div>
<div class="login-card">
<div class="login-title">Welcome back 👋</div>
<div class="login-subtitle">Sign in to continue to NovaAgent</div>

<a href="{login_url}" target="_self" style="text-decoration:none; display:block; margin-bottom: 12px;">
<button class="btn-google">
<img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" class="google-icon" />
Continue with Google
</button>
</a>

{dev_login_html}


</div>

<div class="login-terms-footer">
<span style="cursor: not-allowed; opacity: 0.7;"><span class="footer-icon">🛡️</span> Privacy Policy</span>
<span class="footer-divider">|</span>
<span style="cursor: not-allowed; opacity: 0.7;"><span class="footer-icon">📄</span> Terms of Service</span>
<span class="footer-divider">|</span>
<span style="cursor: not-allowed; opacity: 0.7;"><span class="footer-icon">❓</span> Help Center</span>
</div>
</div>
</div>
""", unsafe_allow_html=True)