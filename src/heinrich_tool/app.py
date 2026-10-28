"""Streamlit web app entry point."""

import logging
from datetime import date
from pathlib import Path

import streamlit as st

from heinrich_tool.backend.input_args import (
    create_delivery_note_args,
    create_invoice_args,
    create_offer_args,
    create_settings,
)
from heinrich_tool.backend.services import (
    generate_delivery_note,
    generate_invoice_and_order,
    generate_offer,
    load_settings,
    save_settings,
)
from heinrich_tool.ui.state import initialize_session_state

logging.basicConfig(
    level=logging.WARNING, format="%(levelname)s (%(name)s): %(message)s"
)
logging.getLogger("heinrich_tool").setLevel(logging.INFO)

ASSETS_DIR = Path(__file__).parent / "assets"

st.set_page_config(
    page_title="Heinrich Tool",
    page_icon=ASSETS_DIR / "icon.ico",
    layout="centered",
)


def run_settings():
    st.session_state.settings_error = None

    try:
        settings = create_settings(
            st.session_state.get("data_root_input", ""),
            st.session_state.get("config_path_input", ""),
            st.session_state.get("template_path_input", ""),
        )
        save_settings(settings)
        st.toast("Pfade gespeichert", icon="✅")
    except (FileNotFoundError, ValueError) as e:
        st.session_state.settings_error = f"Error: {e!s}"
        st.toast("Fehler beim Speichern", icon="❌")


def run_offer(settings):
    st.session_state.offer_info = []
    st.session_state.offer_error = None

    project_number = st.session_state.get("project_number_offer", "")

    try:
        args = create_offer_args(project_number)
        st.session_state.offer_info = generate_offer(args, date.today(), settings)
        st.toast("Angebot erzeugt", icon="✅")
    except (FileNotFoundError, ValueError) as e:
        st.session_state.offer_error = f"Error: {e!s}"
        st.toast("Fehler beim Erzeugen", icon="❌")


def run_delivery(settings):
    st.session_state.delivery_info = []
    st.session_state.delivery_error = None

    project_number = st.session_state.get("project_number_delivery", "")
    receipt_number = st.session_state.get("receipt_number_delivery", "")

    try:
        args = create_delivery_note_args(project_number, receipt_number)
        st.session_state.delivery_info = generate_delivery_note(
            args, date.today(), settings
        )
        st.toast("Lieferschein erzeugt", icon="✅")
    except (FileNotFoundError, ValueError) as e:
        st.session_state.delivery_error = f"Error: {e!s}"
        st.toast("Fehler beim Erzeugen", icon="❌")


def run_invoice(settings):
    st.session_state.invoice_info = []
    st.session_state.invoice_error = None

    project_number = st.session_state.get("project_number_invoice", "")
    receipt_number = st.session_state.get("receipt_number_invoice", "")

    try:
        args = create_invoice_args(project_number, receipt_number)
        st.session_state.invoice_info = generate_invoice_and_order(
            args, date.today(), settings
        )
        st.toast("Rechnung und Auftragsbestätigung erzeugt", icon="✅")
    except (FileNotFoundError, ValueError) as e:
        st.session_state.invoice_error = f"Error: {e!s}"
        st.toast("Fehler beim Erzeugen", icon="❌")


def app():
    st.html(ASSETS_DIR / "style.css")
    initialize_session_state()

    with st.container(gap="xxsmall"):
        st.title("Heinrich Abrechnung")
        st.caption("CSV rein, PDF raus")

    settings = None
    load_error = None
    try:
        settings = load_settings()
    except ValueError as e:
        load_error = f"Error: {e!s}"

    # Stays open while something is missing, so a failed save shows its error.
    expanded = settings is None or bool(st.session_state.settings_error)
    with (
        st.expander("Pfade", expanded=expanded),
        st.form("settings_form", border=False),
    ):
        st.text_input(
            "Datenordner",
            value=str(settings.data_root) if settings else "",
            key="data_root_input",
        )
        st.text_input(
            "Config",
            value=str(settings.config_path) if settings else "",
            key="config_path_input",
        )
        st.text_input(
            "Vordruck",
            value=str(settings.template_path) if settings else "",
            key="template_path_input",
        )

        with st.container(horizontal=True, horizontal_alignment="right"):
            st.form_submit_button("Speichern", on_click=run_settings, type="primary")

        if load_error:
            st.error(load_error)

        if st.session_state.settings_error:
            st.error(st.session_state.settings_error)

    disabled = settings is None
    if disabled:
        st.info("Noch keine Pfade eingestellt.")

    with st.form("offer_form"):
        st.subheader("Angebot")
        st.text_input("Projektnummer", key="project_number_offer", disabled=disabled)

        with st.container(horizontal=True, horizontal_alignment="right"):
            st.form_submit_button(
                "Angebot erzeugen",
                on_click=run_offer,
                args=(settings,),
                type="primary",
                disabled=disabled,
            )

        if st.session_state.offer_info:
            st.code(
                "\n".join(st.session_state.offer_info),
                language="text",
            )

        if st.session_state.offer_error:
            st.error(st.session_state.offer_error)

    with st.form("delivery_form"):
        st.subheader("Lieferschein")
        col1, col2 = st.columns(2)

        with col1:
            st.text_input(
                "Projektnummer", key="project_number_delivery", disabled=disabled
            )

        with col2:
            st.text_input(
                "Belegnummer (optional)",
                key="receipt_number_delivery",
                disabled=disabled,
            )

        with st.container(horizontal=True, horizontal_alignment="right"):
            st.form_submit_button(
                "Lieferschein erzeugen",
                on_click=run_delivery,
                args=(settings,),
                type="primary",
                disabled=disabled,
            )

        if st.session_state.delivery_info:
            st.code(
                "\n".join(st.session_state.delivery_info),
                language="text",
            )

        if st.session_state.delivery_error:
            st.error(st.session_state.delivery_error)

    with st.form("invoice_form"):
        st.subheader("Rechnung & Auftragsbestätigung")
        col1, col2 = st.columns(2)

        with col1:
            st.text_input(
                "Projektnummer", key="project_number_invoice", disabled=disabled
            )

        with col2:
            st.text_input(
                "Belegnummer", key="receipt_number_invoice", disabled=disabled
            )

        with st.container(horizontal=True, horizontal_alignment="right"):
            st.form_submit_button(
                "Rechnung und Auftragsbestätigung erzeugen",
                on_click=run_invoice,
                args=(settings,),
                type="primary",
                disabled=disabled,
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
