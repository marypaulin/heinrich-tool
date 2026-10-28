"""Public API for document generation — orchestrates the full pipeline from CSV to PDF."""

import logging
from datetime import date, timedelta
from pathlib import Path

from heinrich_tool.backend.config import Config, load_config
from heinrich_tool.backend.csv_loader import load_csv_data
from heinrich_tool.backend.csv_transformer import csv_rows_to_line_items
from heinrich_tool.backend.docgen import (
    fill_table_with_line_items,
    load_template,
    replace_placeholders,
    save_docx,
)
from heinrich_tool.backend.input_args import DeliveryNoteArgs, InvoiceArgs, OfferArgs
from heinrich_tool.backend.messages import Messages
from heinrich_tool.backend.models import DocxDeliveryDate, DocxMeta, LineItem, Totals
from heinrich_tool.backend.paths import (
    get_delivery_note_target_path,
    get_invoice_target_path,
    get_latest_csv_path,
    get_offer_target_path,
    get_order_confirmation_target_path,
    get_project_dir,
)
from heinrich_tool.backend.pdfgen import render_pdf
from heinrich_tool.backend.settings import (
    SETTINGS_PATH,
    Settings,
    read_settings,
    write_settings,
)

logger = logging.getLogger(__name__)

# — Private data builders —————————————————————————————————————————————————————


def _build_meta(
    project_number: str,
    receipt_number: str | None,
    document_date: date,
    doc_key: str,
    config: Config,
) -> DocxMeta:
    doc_config = config.documents[doc_key]
    return DocxMeta(
        project_number=project_number,
        receipt_number=receipt_number,
        doctype=doc_config.doctype,
        header=doc_config.header,
        document_date=document_date,
    )


def _build_delivery_date(
    document_date: date, doc_key: str, config: Config
) -> DocxDeliveryDate:
    delivery_days = config.documents[doc_key].delivery_days
    return DocxDeliveryDate(document_date + timedelta(days=delivery_days))


def _load_line_items(
    project_dir: Path,
    config: Config,
    messages: Messages,
) -> list[LineItem]:
    csv_path = get_latest_csv_path(project_dir, config, messages)
    csv_rows = load_csv_data(csv_path, config)
    line_items = csv_rows_to_line_items(csv_rows, config, messages)
    if not line_items:
        raise ValueError(f"No valid rows found in {csv_path.name}")
    return line_items


# — Private document orchestrator —————————————————————————————————————————————


def _generate_document(
    doc_key: str,
    project_number: str,
    receipt_number: str | None,
    document_date: date,
    line_items: list[LineItem],
    target_path: Path,
    template_path: Path,
    config: Config,
    messages: Messages,
    log_label_en: str,
    log_label_de: str,
) -> None:
    """Fill Word template with CSV data and save as DOCX."""
    doc = load_template(template_path)
    meta = _build_meta(project_number, receipt_number, document_date, doc_key, config)
    totals = Totals.calculate_sums_and_vat(line_items, config.vat_rate)
    delivery_date = _build_delivery_date(document_date, doc_key, config)

    fill_table_with_line_items(doc, line_items)
    replace_placeholders(doc, totals.to_mapping())
    replace_placeholders(doc, delivery_date.to_mapping(config.date_format))
    replace_placeholders(doc, meta.to_mapping(config.date_format))
    save_docx(doc, target_path)

    logger.info(f"Generated {log_label_en}: {target_path.name}")
    messages.info(f"{log_label_de} erzeugt ({target_path.name})")


# — Public API ————————————————————————————————————————————————————————————————


def load_settings() -> Settings | None:
    return read_settings(SETTINGS_PATH)


def save_settings(settings: Settings) -> None:
    write_settings(SETTINGS_PATH, settings)


def generate_offer(
    args: OfferArgs, document_date: date, settings: Settings
) -> list[str]:
    """Full pipeline: find project → load CSV → generate Angebot DOCX + PDF."""
    messages = Messages()
    config = load_config(settings.config_path)
    project_dir = get_project_dir(settings.data_root, args.project_number, messages)
    line_items = _load_line_items(project_dir, config, messages)
    target_path = get_offer_target_path(project_dir, args.project_number, config)
    _generate_document(
        doc_key="ANGEBOT",
        project_number=args.project_number,
        receipt_number=None,
        document_date=document_date,
        line_items=line_items,
        target_path=target_path,
        template_path=settings.template_path,
        config=config,
        messages=messages,
        log_label_en="offer",
        log_label_de="Angebot",
    )
    render_pdf(target_path, messages)
    return messages.items


def generate_delivery_note(
    args: DeliveryNoteArgs, document_date: date, settings: Settings
) -> list[str]:
    """Full pipeline: find project → load CSV → generate Lieferschein DOCX + PDF."""
    messages = Messages()
    config = load_config(settings.config_path)
    project_dir = get_project_dir(settings.data_root, args.project_number, messages)
    line_items = _load_line_items(project_dir, config, messages)
    target_path = get_delivery_note_target_path(
        project_dir, args.project_number, config
    )
    _generate_document(
        doc_key="LIEFERSCHEIN",
        project_number=args.project_number,
        receipt_number=args.receipt_number,
        document_date=document_date,
        line_items=line_items,
        target_path=target_path,
        template_path=settings.template_path,
        config=config,
        messages=messages,
        log_label_en="delivery note",
        log_label_de="Lieferschein",
    )
    render_pdf(target_path, messages)
    return messages.items


def generate_invoice_and_order(
    args: InvoiceArgs, document_date: date, settings: Settings
) -> list[str]:
    """Full pipeline: find project → load CSV → generate Rechnung + Auftragsbestätigung DOCX + PDF."""
    messages = Messages()
    config = load_config(settings.config_path)
    project_dir = get_project_dir(settings.data_root, args.project_number, messages)
    line_items = _load_line_items(project_dir, config, messages)
    invoice_path = get_invoice_target_path(
        project_dir, args.project_number, args.receipt_number, config
    )
    order_path = get_order_confirmation_target_path(
        project_dir, args.project_number, args.receipt_number, config
    )
    _generate_document(
        doc_key="RECHNUNG",
        project_number=args.project_number,
        receipt_number=args.receipt_number,
        document_date=document_date,
        line_items=line_items,
        target_path=invoice_path,
        template_path=settings.template_path,
        config=config,
        messages=messages,
        log_label_en="invoice",
        log_label_de="Rechnung",
    )
    _generate_document(
        doc_key="AUFTRAG",
        project_number=args.project_number,
        receipt_number=args.receipt_number,
        document_date=document_date,
        line_items=line_items,
        target_path=order_path,
        template_path=settings.template_path,
        config=config,
        messages=messages,
        log_label_en="order confirmation",
        log_label_de="Auftragsbestätigung",
    )
    render_pdf(invoice_path, messages)
    render_pdf(order_path, messages)
    return messages.items
