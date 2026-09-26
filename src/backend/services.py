"""Public API for document generation — orchestrates the full pipeline from CSV to PDF."""

import logging
from copy import deepcopy
from datetime import date, timedelta
from pathlib import Path

from .config import Config
from .csv_loader import load_csv_data
from .csv_transformer import csv_rows_to_line_items
from .docgen import (
    fill_table_with_line_items,
    load_intermediate_template,
    load_template,
    replace_placeholders,
    save_docx,
    save_intermediate_template,
)
from .input_args import create_delivery_args, create_invoice_args, create_offer_args
from .messages import Messages
from .models import DocxDeliveryDate, DocxMeta, LineItem, Totals
from .paths import (
    get_delivery_target_path,
    get_invoice_target_path,
    get_latest_csv_path,
    get_offer_target_path,
    get_order_target_path,
    get_project_dir,
)
from .pdfgen import render_pdf

# — Private data builders —————————————————————————————————————————————————————


def _build_meta(
    project_number: str,
    receipt_number: str | None,
    doc_key: str,
    config: Config,
) -> DocxMeta:
    doc_config = config.documents[doc_key]
    return DocxMeta(
        project_number=project_number,
        receipt_number=receipt_number,
        doctype=doc_config.doctype,
        header=doc_config.header,
        date_today=date.today(),
    )


def _build_delivery_date(doc_key: str, config: Config) -> DocxDeliveryDate:
    doc_config = config.documents[doc_key]
    assert doc_config.delivery_days is not None  # always set for ANGEBOT/LIEFERSCHEIN
    return DocxDeliveryDate(date.today() + timedelta(days=doc_config.delivery_days))


def _load_line_items(
    project_dir: Path,
    config: Config,
    messages: Messages,
) -> list[LineItem]:
    csv_path, csv_msgs = get_latest_csv_path(project_dir, config)
    messages.items.extend(csv_msgs)
    csv_rows = load_csv_data(csv_path, config)
    line_items, transform_msgs = csv_rows_to_line_items(csv_rows, config)
    messages.items.extend(transform_msgs)
    if not line_items:
        raise ValueError("Keine gültigen Zeilen in der CSV-Datei gefunden.")
    return line_items


# — Private document orchestrators ————————————————————————————————————————————


def _fill_and_save_docx(
    doc,
    meta: DocxMeta,
    target_path: Path,
    config: Config,
    messages: Messages,
    log_label_en: str,
    log_label_de: str,
) -> None:
    """Fill meta placeholders, save as Word DOCX, and log."""
    replace_placeholders(doc, meta.to_mapping(config.date_format))
    save_docx(doc, target_path)
    display_path = target_path.name
    logging.info(f"Generated {log_label_en}: {display_path}")
    messages.info(f"{log_label_de} erzeugt ({display_path})")


def _generate_offer_or_delivery_docx(
    doc_key: str,
    project_number: str,
    receipt_number: str | None,
    line_items: list[LineItem],
    target_path: Path,
    config: Config,
    messages: Messages,
    log_label_en: str,
    log_label_de: str,
) -> None:
    """Fill Word template with CSV data and save as Angebot or Lieferschein DOCX."""
    doc = load_template()
    meta = _build_meta(project_number, receipt_number, doc_key, config)
    totals = Totals.calculate_sums_and_vat(line_items, config.vat_rate)
    delivery_date = _build_delivery_date(doc_key, config)

    fill_table_with_line_items(doc, line_items)
    replace_placeholders(doc, totals.to_mapping())
    replace_placeholders(doc, delivery_date.to_mapping(config.date_format))
    save_intermediate_template(project_number, doc)

    _fill_and_save_docx(
        doc,
        meta,
        target_path,
        config,
        messages,
        log_label_en,
        log_label_de,
    )


def _generate_invoice_and_order_docx(
    project_number: str,
    receipt_number: str,
    target_paths: dict[str, Path],
    config: Config,
    messages: Messages,
) -> None:
    """Generate Rechnung and Auftragsbestaetigung DOCX from intermediate template."""
    doc_invoice = load_intermediate_template(project_number)
    doc_order = deepcopy(doc_invoice)

    meta_invoice = _build_meta(project_number, receipt_number, "RECHNUNG", config)
    meta_order = _build_meta(project_number, receipt_number, "AUFTRAG", config)

    _fill_and_save_docx(
        doc_invoice,
        meta_invoice,
        target_paths["invoice"],
        config,
        messages,
        "invoice",
        "Rechnung",
    )
    _fill_and_save_docx(
        doc_order,
        meta_order,
        target_paths["order"],
        config,
        messages,
        "order confirmation",
        "Auftragsbestätigung",
    )


# — Public API ————————————————————————————————————————————————————————————————


def generate_offer(project_number: str, config: Config) -> list[str]:
    """Full pipeline: validate → find project → load CSV → generate Angebot DOCX + PDF."""
    messages = Messages()
    args = create_offer_args(project_number)
    project_dir, dir_msgs = get_project_dir(config.data_root, args.project_number)
    messages.items.extend(dir_msgs)
    line_items = _load_line_items(project_dir, config, messages)
    target_path = get_offer_target_path(project_dir, args.project_number, config)
    _generate_offer_or_delivery_docx(
        doc_key="ANGEBOT",
        project_number=args.project_number,
        receipt_number=None,
        line_items=line_items,
        target_path=target_path,
        config=config,
        messages=messages,
        log_label_en="offer",
        log_label_de="Angebot",
    )
    render_pdf(target_path, messages)
    return messages.items


def generate_delivery(
    project_number: str,
    receipt_number: str | None,
    config: Config,
) -> list[str]:
    """Full pipeline: validate → find project → load CSV → generate Lieferschein DOCX + PDF."""
    messages = Messages()
    args = create_delivery_args(project_number, receipt_number)
    project_dir, dir_msgs = get_project_dir(config.data_root, args.project_number)
    messages.items.extend(dir_msgs)
    line_items = _load_line_items(project_dir, config, messages)
    target_path = get_delivery_target_path(project_dir, args.project_number, config)
    _generate_offer_or_delivery_docx(
        doc_key="LIEFERSCHEIN",
        project_number=args.project_number,
        receipt_number=args.receipt_number,
        line_items=line_items,
        target_path=target_path,
        config=config,
        messages=messages,
        log_label_en="delivery note",
        log_label_de="Lieferschein",
    )
    render_pdf(target_path, messages)
    return messages.items


def generate_invoice_and_order(
    project_number: str,
    receipt_number: str,
    config: Config,
) -> list[str]:
    """Full pipeline: validate → find project → generate Rechnung + Auftragsbestätigung DOCX + PDF.

    Precondition: an Angebot or Lieferschein must have been generated for this
    project first, as this step reads the intermediate template produced by
    those pipelines."""
    messages = Messages()
    args = create_invoice_args(project_number, receipt_number)
    project_dir, dir_msgs = get_project_dir(config.data_root, args.project_number)
    messages.items.extend(dir_msgs)
    invoice_path = get_invoice_target_path(
        project_dir, args.project_number, args.receipt_number, config
    )
    order_path = get_order_target_path(
        project_dir, args.project_number, args.receipt_number, config
    )
    _generate_invoice_and_order_docx(
        args.project_number,
        args.receipt_number,
        {"invoice": invoice_path, "order": order_path},
        config,
        messages,
    )
    render_pdf(invoice_path, messages)
    render_pdf(order_path, messages)
    return messages.items
