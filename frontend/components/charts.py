import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def apply_plotly_theme(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94A3B8"),
        margin=dict(l=0, r=0, t=30, b=0),
        xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", zeroline=False),
    )
    return fig

def render_usage_chart(data):
    if not data:
        st.info("No usage data available for the last 30 days.")
        return
        
    df = pd.DataFrame(data)
    
    fig = px.line(
        df, x="date", y="used", 
        title="Credit Usage (30 Days)",
        color_discrete_sequence=["#4F7DF3"]
    )
    
    # Fill under the line
    fig.update_traces(fill='tozeroy', fillcolor="rgba(79, 125, 243, 0.1)")
    
    fig = apply_plotly_theme(fig)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

def render_distribution_chart(data):
    if not data:
        st.info("No agent distribution data available.")
        return
        
    df = pd.DataFrame(data)
    
    fig = px.pie(
        df, values="count", names="agent",
        title="Agent Distribution",
        hole=0.6,
        color_discrete_sequence=["#4F7DF3", "#6D5EF7", "#22C55E", "#F59E0B"]
    )
    
    fig = apply_plotly_theme(fig)
    fig.update_traces(textposition='inside', textinfo='percent+label', showlegend=False)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
