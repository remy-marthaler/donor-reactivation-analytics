
import streamlit as st
from src.core.state import get_api_client

from src.core.layout import sidebar_footer
sidebar_footer()

st.title("💰 LTV (Placeholder)")
st.caption("This page will estimate the next-12-month LTV per donor once implemented.")

st.info("TODO: Implement training set generation, regression model (e.g., RandomForestRegressor), and ranking export.")
