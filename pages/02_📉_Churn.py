
import streamlit as st
from src.core.state import get_api_client

from src.core.layout import sidebar_footer
sidebar_footer()

st.title("📉 Churn (Placeholder)")
st.caption("This page will train/predict churn probabilities once implemented.")

st.info("TODO: Implement feature set, model training (e.g., LogisticRegression), and evaluation metrics.")
