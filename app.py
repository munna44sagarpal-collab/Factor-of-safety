from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Coal Pillar Factor of Safety",
    page_icon="⛏️",
    layout="wide",
)

html = (Path(__file__).parent / "static" / "Coal Pillar Factor of Safety.html").read_text(encoding="utf-8")
components.html(html, height=900, scrolling=True)
