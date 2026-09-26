# pages/3_Konfiguration.py
from pathlib import Path

import streamlit as st

st.title("Konfiguration")
st.markdown(
    "Beispielhafte Anzeige von Konfigurationswerten plus Dummy-Button zum Bearbeiten."
)

# Dummy config values for demo
config = {
    "data_root": str(Path.home() / "development" / "heinrich-tool" / "Datenordner"),
    "templates_dir": str(Path.home() / "development" / "heinrich-tool" / "templates"),
    "default_hourly_rate": 55.00,
    "pdf_renderer": "LibreOffice",
    "language": "de-DE",
}

st.subheader("Aktuelle Werte")
st.json(config)

st.divider()
col1, col2 = st.columns([1, 2])
with col1:
    if st.button("Konfiguration bearbeiten", type="primary"):
        st.balloons()
with col2:
    st.caption("Dummy-Button für die Demo. Später: Editor, Validierung, Speichern.")
