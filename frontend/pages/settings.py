import streamlit as st
import time
from frontend.components.layout.navbar import render_navbar
from frontend.utils.api_client import fetch_user_profile, update_user_profile

if "jwt" not in st.session_state:
    st.switch_page("app.py")

jwt = st.session_state["jwt"]

# Re-fetch profile to ensure it's up to date
user = fetch_user_profile(jwt)

if not user:
    st.session_state.clear()
    st.switch_page("app.py")

st.sidebar.markdown("""
    <div style='text-align: center; margin-bottom: 32px;'>
        <img src='app/static/logo.png' width='50' style='margin-bottom: 8px;' />
        <div style='font-weight: 700; font-size: 20px;'>NovaAgent</div>
    </div>
""", unsafe_allow_html=True)

st.sidebar.page_link("app.py", label="Back to Dashboard", icon="🔙")

render_navbar(user_info=user)

st.markdown("<div class='settings-container'>", unsafe_allow_html=True)

# Side Nav
if "settings_tab" not in st.session_state:
    st.session_state.settings_tab = "Profile"
    
tabs = ["Profile", "API Keys", "Notifications", "Billing", "Security"]
col1, col2 = st.columns([1, 3], gap="large")

with col1:
    st.markdown("<div class='settings-nav'>", unsafe_allow_html=True)
    for tab in tabs:
        active_class = "active" if st.session_state.settings_tab == tab else ""
        if st.button(tab, key=f"tab_{tab}", use_container_width=True):
            st.session_state.settings_tab = tab
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='settings-content'>", unsafe_allow_html=True)
    
    if st.session_state.settings_tab == "Profile":
        st.markdown("<h2>Profile Settings</h2>", unsafe_allow_html=True)
        
        with st.form("profile_form"):
            st.markdown("<div class='settings-input-group'><label>Full Name</label>", unsafe_allow_html=True)
            name_input = st.text_input("Name", value=user.get("name", ""), label_visibility="collapsed")
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("<div class='settings-input-group'><label>Email Address</label>", unsafe_allow_html=True)
            st.text_input("Email", value=user.get("email", ""), disabled=True, label_visibility="collapsed")
            st.markdown("<small style='color: var(--text-secondary);'>Email addresses cannot be changed for Google-authenticated accounts.</small>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            submit = st.form_submit_button("Save Changes", type="primary")
            
            if submit:
                if name_input and name_input != user.get("name"):
                    result = update_user_profile(jwt, name_input)
                    if result:
                        st.success("Profile updated successfully!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Failed to update profile.")
                else:
                    st.info("No changes to save.")
                    
    elif st.session_state.settings_tab == "API Keys":
        st.markdown("<h2>API Keys</h2><p style='color: var(--text-secondary);'>Manage your secret API keys to access NovaAgent programmatically.</p>", unsafe_allow_html=True)
        st.button("Generate New Key", type="primary")
        
    elif st.session_state.settings_tab == "Notifications":
        st.markdown("<h2>Notifications</h2><p style='color: var(--text-secondary);'>Configure how you receive alerts and updates.</p>", unsafe_allow_html=True)
        st.checkbox("Email me when an agent finishes a long task", value=True)
        st.checkbox("Send weekly usage report", value=False)
        
    elif st.session_state.settings_tab == "Billing":
        st.markdown("<h2>Billing Overview</h2><p style='color: var(--text-secondary);'>Manage your plan and payment methods.</p>", unsafe_allow_html=True)
        st.page_link("pages/billing.py", label="Go to detailed Billing page")
        
    elif st.session_state.settings_tab == "Security":
        st.markdown("<h2>Security</h2><p style='color: var(--text-secondary);'>Review your account security and sessions.</p>", unsafe_allow_html=True)
        st.info("You are currently authenticated via Google OAuth.")
        
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
