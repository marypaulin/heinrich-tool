"""DOCX-to-PDF conversion via Word (Windows) or LibreOffice (Linux)."""

import contextlib
import logging
import platform
import shutil
import subprocess
import threading
from pathlib import Path

from docx2pdf import convert

from heinrich_tool.backend.messages import Messages

logger = logging.getLogger(__name__)

# Ensure Word conversion runs strictly one-at-a-time (Streamlit reruns / double clicks can parallelize)
_WORD_CONVERT_LOCK = threading.Lock()


def render_pdf(docx_path: Path, messages: Messages) -> None:
    """Convert DOCX file to PDF using Word on Windows or LibreOffice on Linux."""

    pdf_path = docx_path.with_suffix(".pdf")
    system = platform.system()

    # --------------------
    # Windows: Microsoft Word via docx2pdf
    # --------------------
    if system == "Windows":
        # Most common failure: existing/open PDF blocks overwrite
        if pdf_path.exists():
            try:
                pdf_path.unlink()
            except PermissionError:
                messages.error(
                    f"PDF konnte nicht überschrieben werden, Datei evtl. geöffnet ({pdf_path.name})"
                )
                logger.exception(f"PDF locked / cannot delete: {pdf_path}")
                return

        # COM init is required per-thread on Windows. Streamlit may execute in a thread without COM initialized.
        try:
            import pythoncom  # type: ignore  # provided by pywin32
        except ImportError:
            pythoncom = None

        try:
            with _WORD_CONVERT_LOCK:
                if pythoncom is not None:
                    pythoncom.CoInitialize()

                # More robust: output directory instead of output file
                convert(str(docx_path), str(docx_path.parent))

                # docx2pdf can fail silently -> verify output exists
                if not pdf_path.exists():
                    messages.error(
                        "PDF wurde nicht erzeugt, bitte prüfen, ob Word installiert "
                        "ist, die Datei nicht geöffnet ist und keine WINWORD.EXE hängt"
                    )
                    logger.error(f"docx2pdf finished without creating pdf: {pdf_path}")
                    return

            messages.info(f"PDF erzeugt ({pdf_path.name})")
            logger.info(f"Generated PDF document via Word: {pdf_path.name}")
            return

        except Exception as e:
            messages.error(f"PDF-Erzeugung fehlgeschlagen ({e})")
            logger.exception("Word-based PDF conversion failed")
            return

        finally:
            if pythoncom is not None:
                with contextlib.suppress(Exception):
                    pythoncom.CoUninitialize()

    # --------------------
    # Linux: LibreOffice (headless)
    # --------------------
    elif system == "Linux":
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

            if not pdf_path.exists():
                messages.error(
                    "PDF wurde nicht erzeugt, LibreOffice-Konvertierung fehlgeschlagen"
                )
                logger.error(f"LibreOffice finished without creating pdf: {pdf_path}")
                return

            messages.info(f"PDF erzeugt ({pdf_path.name})")
            logger.info(f"Generated PDF document via LibreOffice: {pdf_path.name}")
            return

        except subprocess.CalledProcessError as e:
            messages.error(f"LibreOffice-PDF-Erzeugung fehlgeschlagen ({e})")
            logger.exception("LibreOffice PDF conversion failed")
            return

    # --------------------
    # Unsupported system
    # --------------------
    messages.error("PDF-Erzeugung wird auf diesem Betriebssystem nicht unterstützt")
    logger.error(f"PDF generation not supported on system: {system}")
