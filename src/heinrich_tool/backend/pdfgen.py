"""DOCX-to-PDF conversion via Word (Windows) or LibreOffice (Linux)."""

import logging
import platform
import shutil
import subprocess
import threading
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

from heinrich_tool.backend.messages import Messages

logger = logging.getLogger(__name__)

# One Word conversion at a time: Streamlit reruns and double clicks run in parallel
_WORD_CONVERT_LOCK = threading.Lock()

# Word constants, named as in Word's object model
WD_ALERTS_NONE = 0
WD_EXPORT_FORMAT_PDF = 17
WD_DO_NOT_SAVE_CHANGES = 0


def render_pdf(docx_path: Path, messages: Messages) -> None:
    system = platform.system()
    if system == "Windows":
        _render_with_word(docx_path, messages)
    elif system == "Linux":
        _render_with_libreoffice(docx_path, messages)
    else:
        messages.error("PDF-Erzeugung wird auf diesem Betriebssystem nicht unterstützt")
        logger.error(f"PDF generation not supported on system: {system}")


@contextmanager
def _com_initialized() -> Generator[None]:
    # COM init is required per thread; Streamlit runs callbacks in worker threads
    import pythoncom  # type: ignore  # pywin32, Windows only

    # Uninitialize only after successful init, COM counts the calls per thread
    pythoncom.CoInitialize()
    try:
        yield
    finally:
        pythoncom.CoUninitialize()


def _render_with_word(docx_path: Path, messages: Messages) -> None:
    pdf_path = docx_path.with_suffix(".pdf")

    # Most common failure: existing/open PDF blocks overwrite
    if pdf_path.exists():
        try:
            pdf_path.unlink()
        except PermissionError:
            messages.error(
                f"PDF kann nicht gespeichert werden, evtl noch geöffnet ({pdf_path.name})"
            )
            logger.exception(f"PDF locked / cannot delete: {pdf_path}")
            return

    try:
        with _WORD_CONVERT_LOCK, _com_initialized():
            _export_with_word(docx_path, pdf_path)

        messages.info(f"PDF erzeugt ({pdf_path.name})")
        logger.info(f"Generated PDF document via Word: {pdf_path.name}")

    except Exception as e:
        messages.error(f"PDF-Erzeugung fehlgeschlagen ({e})")
        logger.exception("Word-based PDF conversion failed")


def _export_with_word(docx_path: Path, pdf_path: Path) -> None:
    import win32com.client  # type: ignore  # pywin32, Windows only

    # Own Word process: Dispatch would attach to a Word the user has open, and
    # Quit would then close the user's documents too
    word = win32com.client.DispatchEx("Word.Application")
    try:
        word.DisplayAlerts = WD_ALERTS_NONE
        doc = word.Documents.Open(
            str(docx_path.resolve()), ReadOnly=True, AddToRecentFiles=False
        )
        try:
            doc.ExportAsFixedFormat(
                str(pdf_path.resolve()), ExportFormat=WD_EXPORT_FORMAT_PDF
            )
        finally:
            doc.Close(SaveChanges=WD_DO_NOT_SAVE_CHANGES)
    finally:
        word.Quit()


def _render_with_libreoffice(docx_path: Path, messages: Messages) -> None:
    pdf_path = docx_path.with_suffix(".pdf")

    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        messages.error("LibreOffice nicht gefunden, bitte LibreOffice installieren")
        logger.error("LibreOffice (soffice) not found")
        return

    try:
        subprocess.run(
            [
                soffice,
                "--headless",
                "--nologo",
                "--nodefault",
                "--nofirststartwizard",
                "--convert-to",
                "pdf",
                "--outdir",
                str(docx_path.parent),
                str(docx_path),
            ],
            check=True,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError as e:
        messages.error(f"LibreOffice-PDF-Erzeugung fehlgeschlagen ({e})")
        logger.exception("LibreOffice PDF conversion failed")
        return

    if not pdf_path.exists():
        messages.error(
            "PDF wurde nicht erzeugt, LibreOffice-Konvertierung fehlgeschlagen"
        )
        logger.error(f"LibreOffice finished without creating pdf: {pdf_path}")
        return

    messages.info(f"PDF erzeugt ({pdf_path.name})")
    logger.info(f"Generated PDF document via LibreOffice: {pdf_path.name}")
