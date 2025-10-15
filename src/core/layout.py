# src/core/layout.py
import streamlit as st
from src.core.state import get_api_client

def sidebar_footer():
    st.markdown("""
    <style>
    section[data-testid="stSidebar"] > div {
      height: 100%; display: flex; flex-direction: column;
    }
    .sidebar-footer {
      margin-top: auto; padding-top: .75rem;
      font-size: .85rem;
    }
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        api = get_api_client()
        st.markdown(
            f'<div class="sidebar-footer">API client in use: '
            f'<code>{type(api).__name__}</code></div>',
            unsafe_allow_html=True
        )
