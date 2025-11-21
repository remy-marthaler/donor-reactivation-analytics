
import streamlit as st

from st_pages import add_page_title, get_nav_from_toml
from src.core.layout import sidebar_footer

sidebar_footer()

nav = get_nav_from_toml(".streamlit/pages.toml")
pg = st.navigation(nav)
add_page_title(pg)
st.set_page_config(layout="wide")
pg.run()
