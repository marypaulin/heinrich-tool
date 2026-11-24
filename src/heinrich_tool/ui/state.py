"""Streamlit session state initialization."""

import streamlit as st


def initialize_session_state() -> None:
    if "settings_error" not in st.session_state:
        st.session_state.settings_error = None
    if "generate_info" not in st.session_state:
        st.session_state.generate_info = []
    if "generate_error" not in st.session_state:
        st.session_state.generate_error = None
