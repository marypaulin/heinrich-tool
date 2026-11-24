"""Public API for document generation — orchestrates the full pipeline from CSV to PDF."""

import logging
from datetime import date, timedelta
from pathlib import Path

from heinrich_tool.backend.config import Config, DocumentKind, read_config
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
from heinrich_tool.backend.models import DocumentMeta, LineItem, Totals
from heinrich_tool.backend.paths import (
    get_latest_csv_path,
    get_project_dir,
    get_target_path,
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
    delivery_date: date,
    kind: DocumentKind,
    config: Config,
) -> DocumentMeta:
    doc_config = config.document(kind)
    return DocumentMeta(
        project_number=project_number,
        receipt_number=receipt_number,
        doctype=doc_config.doctype,
        header=doc_config.header,
        document_date=document_date,
        delivery_date=delivery_date,
    )


def _build_delivery_date(
    document_date: date, kind: DocumentKind, config: Config
) -> date:
    delivery_days = config.document(kind).delivery_days
    return document_date + timedelta(days=delivery_days)


def _load_line_items(
    project_dir: Path,
    config: Config,
    messages: Messages,
) -> list[LineItem]:
    csv_path = get_latest_csv_path(project_dir, config, messages)
    csv_rows = load_csv_data(csv_path)
    line_items = csv_rows_to_line_items(csv_rows, config, messages)
    if not line_items:
        raise ValueError(f"No valid rows found in {csv_path.name}")
    return line_items


# — Private document orchestrator —————————————————————————————————————————————


def _generate_document(
    kind: DocumentKind,
    project_dir: Path,
    project_number: str,
    receipt_number: str | None,
    document_date: date,
    line_items: list[LineItem],
    template_path: Path,
    config: Config,
    messages: Messages,
) -> Path:
    target_path = get_target_path(
        project_dir, kind, config, project_number, receipt_number
    )
    doc = load_template(template_path)
    delivery_date = _build_delivery_date(document_date, kind, config)
    meta = _build_meta(
        project_number, receipt_number, document_date, delivery_date, kind, config
    )
    totals = Totals.from_line_items(line_items, config.vat_rate)

    fill_table_with_line_items(doc, line_items)
    replace_placeholders(doc, totals.to_mapping() | meta.to_mapping(config.date_format))
    save_docx(doc, target_path)

    log_label = kind.replace("_", " ")
    logger.info(f"Generated {log_label}: {target_path.name}")
    messages.info(f"{meta.doctype} erzeugt ({target_path.name})")
    return target_path


# — Public API ————————————————————————————————————————————————————————————————


def load_settings() -> Settings | None:
    return read_settings(SETTINGS_PATH)


def save_settings(settings: Settings) -> None:
    write_settings(SETTINGS_PATH, settings)


def generate_offer(
    args: OfferArgs, document_date: date, settings: Settings
) -> Messages:
    messages = Messages()
    config = read_config(settings.config_path)
    project_dir = get_project_dir(settings.data_root, args.project_number, messages)
    line_items = _load_line_items(project_dir, config, messages)
    target_path = _generate_document(
        kind=DocumentKind.OFFER,
        project_dir=project_dir,
        project_number=args.project_number,
        receipt_number=None,
        document_date=document_date,
        line_items=line_items,
        template_path=settings.template_path,
        config=config,
        messages=messages,
    )
    render_pdf(target_path, messages)
    return messages


def generate_delivery_note(
    args: DeliveryNoteArgs, document_date: date, settings: Settings
) -> Messages:
    messages = Messages()
    config = read_config(settings.config_path)
    project_dir = get_project_dir(settings.data_root, args.project_number, messages)
    line_items = _load_line_items(project_dir, config, messages)
    target_path = _generate_document(
        kind=DocumentKind.DELIVERY_NOTE,
        project_dir=project_dir,
        project_number=args.project_number,
        receipt_number=args.receipt_number,
        document_date=document_date,
        line_items=line_items,
        template_path=settings.template_path,
        config=config,
        messages=messages,
    )
    render_pdf(target_path, messages)
    return messages


def generate_invoice_and_order(
    args: InvoiceArgs, document_date: date, settings: Settings
) -> Messages:
    messages = Messages()
    config = read_config(settings.config_path)
    project_dir = get_project_dir(settings.data_root, args.project_number, messages)
    line_items = _load_line_items(project_dir, config, messages)
    invoice_path = _generate_document(
        kind=DocumentKind.INVOICE,
        project_dir=project_dir,
        project_number=args.project_number,
        receipt_number=args.receipt_number,
        document_date=document_date,
        line_items=line_items,
        template_path=settings.template_path,
        config=config,
        messages=messages,
    )
    order_path = _generate_document(
        kind=DocumentKind.ORDER_CONFIRMATION,
        project_dir=project_dir,
        project_number=args.project_number,
        receipt_number=args.receipt_number,
        document_date=document_date,
        line_items=line_items,
        template_path=settings.template_path,
        config=config,
        messages=messages,
    )
    render_pdf(invoice_path, messages)
    render_pdf(order_path, messages)
    return messages
