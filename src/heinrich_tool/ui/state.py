"""Streamlit session state initialisation."""

import streamlit as st


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
