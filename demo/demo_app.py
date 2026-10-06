# app.py
import streamlit as st

st.set_page_config(
    page_title="Heinrich Tool",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.title("Heinrich Tool")

st.markdown("""
Wähle links eine Seite aus:

- Dokumente erzeugen
- E-Rechnung
- Konfiguration
""")
