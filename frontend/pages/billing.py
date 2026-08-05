import datetime

import streamlit as st

st.set_page_config(layout="wide", initial_sidebar_state="expanded")

from frontend.components.layout.shell import render_sidebar, render_topbar
from frontend.utils.api_client import (
    fetch_balance,
    fetch_transactions,
    fetch_user_profile,
)
from frontend.utils.css_loader import load_all_css

load_all_css()


def render_billing():

    if "jwt" not in st.session_state:
        st.switch_page("app.py")

    jwt = st.session_state["jwt"]
    user = fetch_user_profile(jwt)

    if not user:
        st.session_state.clear()
        st.switch_page("app.py")

    balance_data = fetch_balance(jwt)
    credits = balance_data.get("credits", 0) if balance_data else 0
    user_for_shell = {**user, "credits": credits}

    render_sidebar(active="billing", user=user_for_shell)
    render_topbar(icon="💳", title="Billing & Credits", subtitle="Manage your plan, credits and billing information", user=user_for_shell)
    st.markdown("<div class='nova-page-header-spacer'></div>", unsafe_allow_html=True)

    st.markdown("<div class='billing-container'>", unsafe_allow_html=True)

    usage_pct = max(0, min(100, ((100 - credits) / 100) * 100)) # Base 100 max

    st.markdown(f"""
<div class="billing-balance-card">
<h2>Current Balance</h2>
<p style="font-size: 36px; font-weight: 700; margin: 8px 0;">{credits} <span style="font-size: 16px; font-weight: 400; color: var(--text-secondary);">credits remaining</span></p>
<div class="billing-usage-bar">
<div class="billing-usage-fill" style="width: {usage_pct}%"></div>
</div>
<p style="color: var(--text-secondary); margin-top: 8px; font-size: 12px;">Monthly allowance resets in 14 days.</p>
</div>
    """, unsafe_allow_html=True)

    st.markdown("<h2>Plans</h2>", unsafe_allow_html=True)
    st.markdown("""
<div class="billing-plans-grid">
<div class="billing-plan-card">
<h3>Free</h3>
<p style="font-size: 24px; font-weight: 700;">$0<span style="font-size: 14px; font-weight: 400; color: var(--text-secondary);">/mo</span></p>
<p style="color: var(--text-secondary); font-size: 14px;">100 credits included</p>
<button style="margin-top: auto; padding: 12px; background: transparent; border: 1px solid var(--accent-primary); color: var(--accent-primary); border-radius: 12px; cursor: pointer;">Current Plan</button>
</div>

<div class="billing-plan-card pro">
<h3>Pro</h3>
<p style="font-size: 24px; font-weight: 700;">$15<span style="font-size: 14px; font-weight: 400; color: var(--text-secondary);">/mo</span></p>
<p style="color: var(--text-secondary); font-size: 14px;">1000 credits included</p>
<button style="margin-top: auto; padding: 12px; background: var(--accent-gradient); color: white; border: none; border-radius: 12px; cursor: pointer;">Upgrade to Pro</button>
</div>

<div class="billing-plan-card">
<h3>Enterprise</h3>
<p style="font-size: 24px; font-weight: 700;">Custom</p>
<p style="color: var(--text-secondary); font-size: 14px;">Unlimited credits & dedicated agents</p>
<button style="margin-top: auto; padding: 12px; background: transparent; border: 1px solid var(--border); color: var(--text-primary); border-radius: 12px; cursor: pointer;">Contact Sales</button>
</div>
</div>
    """, unsafe_allow_html=True)

    st.markdown("<h2>Transaction History</h2>", unsafe_allow_html=True)

    transactions = fetch_transactions(jwt)

    if not transactions:
        st.info("No recent transactions.")
    else:
        table_html = """
<table class="billing-tx-table">
    <thead>
        <tr>
            <th>Date</th>
            <th>Description</th>
            <th>Agent</th>
            <th style="text-align: right;">Amount</th>
            <th style="text-align: right;">Balance After</th>
        </tr>
    </thead>
    <tbody>
"""
    
        for tx in transactions:
            dt = datetime.datetime.fromisoformat(tx['created_at']).strftime("%Y-%m-%d %H:%M")
            amount_cls = "negative" if tx['amount'] < 0 else "positive"
            sign = "+" if tx['amount'] > 0 else ""
            table_html += f"""<tr>
    <td style="color: var(--text-secondary);">{dt}</td>
    <td>{tx['description']}</td>
    <td style="color: var(--text-secondary);">{tx['agent_type'] or '-'}</td>
    <td style="text-align: right;" class="tx-amount {amount_cls}">{sign}{tx['amount']}</td>
    <td style="text-align: right;">{tx['balance_after']}</td>
</tr>"""
        
        table_html += "</tbody></table>"
        st.markdown(table_html, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


render_billing()
