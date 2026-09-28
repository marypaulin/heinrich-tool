"""Streamlit web app entry point."""

import streamlit as st

from src.backend.input_args import (
    create_delivery_args,
    create_invoice_args,
    create_offer_args,
)
from src.backend.services import (
    generate_delivery,
    generate_invoice_and_order,
    generate_offer,
)
from src.ui.state import get_config, initialize_session_state

st.set_page_config(
    page_title="Heinrich App",
    page_icon="assets/icon.ico",
    layout="centered",
)


def suppress_round_corners():
    st.markdown(
        """
        <style>
        img {
            border-radius: 0 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def run_offer(config):
    st.session_state.offer_info = []
    st.session_state.offer_error = None

    project_number = st.session_state.get("project_number_offer", "")

    try:
        args = create_offer_args(project_number)
        st.session_state.offer_info = generate_offer(args, config)
        st.toast("Angebot erzeugt", icon="✅")
    except (FileNotFoundError, ValueError) as e:
        st.session_state.offer_error = f"Error: {e!s}"
        st.toast("Fehler beim Erzeugen", icon="❌")


def run_delivery(config):
    st.session_state.delivery_info = []
    st.session_state.delivery_error = None

    project_number = st.session_state.get("project_number_delivery", "")
    receipt_number = st.session_state.get("receipt_number_delivery", "")

    try:
        args = create_delivery_args(project_number, receipt_number)
        st.session_state.delivery_info = generate_delivery(args, config)
        st.toast("Lieferschein erzeugt", icon="✅")
    except (FileNotFoundError, ValueError) as e:
        st.session_state.delivery_error = f"Error: {e!s}"
        st.toast("Fehler beim Erzeugen", icon="❌")


def run_invoice(config):
    st.session_state.invoice_info = []
    st.session_state.invoice_error = []

    project_number = st.session_state.get("project_number_invoice", "")
    receipt_number = st.session_state.get("receipt_number_invoice", "")

    try:
        args = create_invoice_args(project_number, receipt_number)
        st.session_state.invoice_info = generate_invoice_and_order(args, config)
        st.toast("Rechnung und Auftragsbestätigung erzeugt", icon="✅")
    except (FileNotFoundError, ValueError) as e:
        st.session_state.invoice_error = f"Error: {e!s}"
        st.toast("Fehler beim Erzeugen", icon="❌")


def app():
    suppress_round_corners()
    config = get_config()
    initialize_session_state()

    # Logo
    col1, _, col2 = st.columns(3)
    with col2:
        st.image("assets/logo.png")

    # Title
    st.title("Projektabrechnung")

    # Introduction
    st.markdown(
        "Erstelle **Angebote**, **Lieferscheine**, **Rechnungen** und **Auftragsbestätigungen** "
        "direkt aus deinen Zeiterfassungsdaten."
    )

    # Angebot
    st.subheader("Angebot")

    with st.form("offer_form"):
        col1, _ = st.columns(2)

        with col1:
            st.text_input(
                "Bitte Projektnummer eingeben",
                key="project_number_offer",
            )

        st.form_submit_button(
            "Angebot erzeugen",
            on_click=run_offer,
            args=(config,),
        )

        if st.session_state.offer_info:
            st.code(
                "\n".join(st.session_state.offer_info),
                language="text",
            )

        if st.session_state.offer_error:
            st.error(st.session_state.offer_error)

    # Lieferschein
    st.subheader("Lieferschein")

    with st.form("delivery_form"):
        col1, col2 = st.columns(2)

        with col1:
            st.text_input(
                "Bitte Projektnummer eingeben",
                key="project_number_delivery",
            )

        with col2:
            st.text_input(
                "Optional Belegnummer eingeben",
                key="receipt_number_delivery",
            )

        st.form_submit_button(
            "Lieferschein erzeugen",
            on_click=run_delivery,
            args=(config,),
        )

        if st.session_state.delivery_info:
            st.code(
                "\n".join(st.session_state.delivery_info),
                language="text",
            )

        if st.session_state.delivery_error:
            st.error(st.session_state.delivery_error)

    # Rechnung / Auftragsbestätigung
    st.subheader("Rechnung & Auftragsbestätigung")

    with st.form("invoice_form"):
        col1, col2 = st.columns(2)

        with col1:
            st.text_input(
                "Bitte Projektnummer eingeben",
                key="project_number_invoice",
            )

        with col2:
            st.text_input(
                "Bitte Belegnummer eingeben",
                key="receipt_number_invoice",
            )

        st.form_submit_button(
            "Rechnung und Auftragsbestätigung erzeugen",
            on_click=run_invoice,
            args=(config,),
        )

        if st.session_state.invoice_info:
            st.code(
                "\n".join(st.session_state.invoice_info),
                language="text",
            )

        if st.session_state.invoice_error:
            st.error(st.session_state.invoice_error)


if __name__ == "__main__":
    app()
