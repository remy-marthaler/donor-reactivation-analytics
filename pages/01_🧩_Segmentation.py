#Kay
import streamlit as st
from src.core.state import get_api_client

from src.core.layout import sidebar_footer
sidebar_footer()

st.title("🧩 Segmentation (Placeholder)")
st.caption("This page will segment donors into clusters once implemented.")

st.info("TODO: Implement feature engineering, KMeans, and a results table/plot.")
