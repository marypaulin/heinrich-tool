"""Streamlit web app entry point."""

import logging
from datetime import date
from pathlib import Path

import streamlit as st

from heinrich_tool.backend.config import DocumentKind
from heinrich_tool.backend.input_args import create_document_args, create_settings
from heinrich_tool.backend.services import (
    generate_document,
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

DOCUMENT_LABELS = {
    DocumentKind.OFFER: "Angebot",
    DocumentKind.DELIVERY_NOTE: "Lieferschein",
    DocumentKind.INVOICE: "Rechnung",
    DocumentKind.ORDER_CONFIRMATION: "Auftragsbestätigung",
}


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
        st.session_state.settings_error = f"Fehler: {e!s}"
        st.toast("Fehler beim Speichern", icon="❌")


def toast_result(document, messages):
    # Failed PDF leaves DOCX intact, so generation counts as done but not clean
    if messages.has_errors:
        st.toast(f"{document} erzeugt, mit Fehlern", icon="⚠️")
    else:
        st.toast(f"{document} erzeugt", icon="✅")


def run_generate(settings):
    st.session_state.generate_info = []
    st.session_state.generate_error = None

    kind = st.session_state.document_kind
    project_number = st.session_state.get("project_number", "")
    receipt_number = st.session_state.get("receipt_number", "")

    try:
        args = create_document_args(kind, project_number, receipt_number)
        messages = generate_document(args, date.today(), settings)
        st.session_state.generate_info = [str(m) for m in messages.items]
        toast_result(DOCUMENT_LABELS[kind], messages)
    except (FileNotFoundError, ValueError) as e:
        st.session_state.generate_error = f"Fehler: {e!s}"
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
        load_error = f"Fehler: {e!s}"

    # Stays open while something is missing, so a failed save shows its error
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
        st.info("Noch keine Pfade eingestellt")

    with st.form("document_form"):
        col1, _ = st.columns(2)

        with col1:
            st.selectbox(
                "Dokument",
                options=list(DocumentKind),
                format_func=DOCUMENT_LABELS.__getitem__,
                key="document_kind",
                disabled=disabled,
            )

        col1, col2 = st.columns(2)

        with col1:
            st.text_input("Projektnummer", key="project_number", disabled=disabled)

        with col2:
            st.text_input("Belegnummer", key="receipt_number", disabled=disabled)

        with st.container(horizontal=True, horizontal_alignment="right"):
            st.form_submit_button(
                "Erzeugen",
                on_click=run_generate,
                args=(settings,),
                type="primary",
                disabled=disabled,
            )

        if st.session_state.generate_info:
            st.code(
                "\n".join(st.session_state.generate_info),
                language="text",
            )

        if st.session_state.generate_error:
            st.error(st.session_state.generate_error)


if __name__ == "__main__":
    app()
