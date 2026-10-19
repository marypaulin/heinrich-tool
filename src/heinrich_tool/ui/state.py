"""Streamlit session state initialisation and config caching."""

import streamlit as st

from heinrich_tool.backend.config import Config, load_config
from heinrich_tool.backend.paths import CONFIG_PATH


def get_config() -> Config:
    return st.session_state.setdefault("config", load_config(CONFIG_PATH))


def initialize_session_state() -> None:
    if "offer_info" not in st.session_state:
        st.session_state.offer_info = []
    if "offer_error" not in st.session_state:
        st.session_state.offer_error = None
    if "delivery_info" not in st.session_state:
        st.session_state.delivery_info = []
    if "delivery_error" not in st.session_state:
        st.session_state.delivery_error = None
    if "invoice_info" not in st.session_state:
        st.session_state.invoice_info = []
    if "invoice_error" not in st.session_state:
        st.session_state.invoice_error = None
