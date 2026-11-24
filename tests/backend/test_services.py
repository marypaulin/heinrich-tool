"""End-to-end tests: sample CSV in, finished Word documents out."""

import re
import shutil
from datetime import date
from pathlib import Path

import pytest
from docx import Document
from docx.document import Document as DocxDocument
from docx.table import Table, _Cell

from heinrich_tool.backend import services
from heinrich_tool.backend.config import DocumentKind
from heinrich_tool.backend.input_args import create_document_args
from heinrich_tool.backend.messages import Level
from heinrich_tool.backend.services import generate_document
from heinrich_tool.backend.settings import Settings
from samples import (
    SAMPLE_CONFIG_PATH,
    SAMPLE_CSV_PATH,
    SAMPLE_TEMPLATE_PATH,
    write_variant,
)

PROJECT_FOLDER = "1234 - Schutzgitter Mischer 3"

# CSV row 11 has a blank order number and is skipped
ITEM_ROWS = [
    ["1", "1", "Meisterstunde zu Auftrag Nr. 123", "84,90€", "84,90€"],
    ["2", "11", "Meisterstunde zu Auftrag Nr. 90010001", "84,90€", "933,90€"],
    ["3", "5", "Meisterstunde zu Auftrag Nr. 90010002", "84,90€", "424,50€"],
    ["4", "7", "Meisterstunde zu Auftrag Nr. 90010003", "84,90€", "594,30€"],
    ["5", "4", "Meisterstunde Sonntag zu Auftrag Nr. 90010003", "139,90€", "559,60€"],
    ["6", "7", "Helferstunde zu Auftrag Nr. 111", "48,00€", "336,00€"],
    ["7", "3", "Helferstunde zu Auftrag Nr. 111", "48,00€", "144,00€"],
    ["8", "2,5", "Meisterstunde zu Auftrag Nr. 90010004", "84,90€", "212,25€"],
    ["9", "2", "Meisterstunde zu Auftrag Nr. 90010005", "84,90€", "169,80€"],
    ["10", "1", "Material zu Auftrag Nr. 123", "95,00€", "95,00€"],
    ["11", "1", "Material zu Auftrag Nr. 111", "30,00€", "30,00€"],
    ["12", "1", "Material zu Auftrag Nr. 111", "270,00€", "270,00€"],
    ["13", "1", "Material zu Auftrag Nr. 90010006", "145,00€", "145,00€"],
]

SUM_ROWS = [
    ["Summe", "Summe", "", "", "3.999,25€"],
    [*["Ust. 19% auf 3.999,25€ netto"] * 3, "", "759,86€"],
    [*["Gesamtbetrag"] * 3, "", "4.759,11€"],
]


@pytest.fixture(autouse=True)
def no_pdf(monkeypatch):
    """PDF rendering is checked by hand."""
    monkeypatch.setattr(services, "render_pdf", lambda docx_path, messages: None)


@pytest.fixture
def sample_data_root(tmp_path) -> Path:
    """Data root in `tmp_path` with one project folder holding the sample CSV."""
    data_root = tmp_path / "Daten"
    project_dir = data_root / PROJECT_FOLDER
    project_dir.mkdir(parents=True)
    shutil.copy(SAMPLE_CSV_PATH, project_dir)
    return data_root


@pytest.fixture
def sample_settings(sample_data_root) -> Settings:
    return Settings(
        data_root=sample_data_root,
        config_path=SAMPLE_CONFIG_PATH,
        template_path=SAMPLE_TEMPLATE_PATH,
    )


def open_document(data_root: Path, filename: str) -> DocxDocument:
    return Document(str(data_root / PROJECT_FOLDER / filename))


def info_block(doc: DocxDocument) -> _Cell:
    return doc.tables[1].cell(1, 2)


def item_table(doc: DocxDocument) -> Table:
    return doc.tables[2]


def item_table_rows(doc: DocxDocument) -> list[list[str]]:
    return [[cell.text for cell in row.cells] for row in item_table(doc).rows[1:]]


def texts(doc: DocxDocument) -> list[str]:
    """Paragraph texts of the body and the info block."""
    return [p.text for p in doc.paragraphs + info_block(doc).paragraphs]


def assert_items_and_sums(doc: DocxDocument) -> None:
    assert item_table_rows(doc) == ITEM_ROWS + SUM_ROWS


def assert_no_placeholders_left(doc: DocxDocument) -> None:
    """Catches placeholders the code does not know, too, not only the known ones."""
    paragraphs = list(doc.paragraphs)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                paragraphs.extend(cell.paragraphs)
    for section in doc.sections:
        paragraphs.extend(section.header.paragraphs)
        paragraphs.extend(section.footer.paragraphs)
    leftovers = [m for p in paragraphs for m in re.findall(r"<[^<>]+>", p.text)]
    assert leftovers == []


# — Angebot ———————————————————————————————————————————————————————————————————


def test_offer(sample_settings, sample_data_root):
    args = create_document_args(DocumentKind.OFFER, "1234", None, date(2025, 8, 15))
    generate_document(args, date(2025, 8, 1), sample_settings)

    doc = open_document(sample_data_root, "Angebot Nr. 1234.docx")
    doc_texts = texts(doc)
    assert_items_and_sums(doc)
    assert_no_placeholders_left(doc)
    assert "Datum:\t01.08.2025" in doc_texts
    assert "Angebot Nr. 1234 – " in doc_texts
    assert "Auftragsnummer:\t1234 / " in doc_texts
    assert (
        "Vielen Dank für ihr Vertrauen in Heinrich Metallbau. "
        "Wir bieten folgende Positionen an: "
    ) in doc_texts
    assert "Liefertermin: 15.08.2025" in doc_texts


def test_failed_pdf_is_reported_to_caller(monkeypatch, sample_settings):
    monkeypatch.setattr(
        services,
        "render_pdf",
        lambda docx_path, messages: messages.error("PDF-Erzeugung fehlgeschlagen"),
    )
    args = create_document_args(DocumentKind.OFFER, "1234", None, date(2025, 8, 15))
    messages = generate_document(args, date(2025, 8, 1), sample_settings)
    assert messages.has_errors


def test_offer_leaves_out_receipt_number_and_warns(sample_settings, sample_data_root):
    args = create_document_args(
        DocumentKind.OFFER, "1234", "4100012345", date(2025, 8, 15)
    )
    messages = generate_document(args, date(2025, 8, 1), sample_settings)

    doc_texts = texts(open_document(sample_data_root, "Angebot Nr. 1234.docx"))
    assert "Angebot Nr. 1234 – " in doc_texts
    assert "Auftragsnummer:\t1234 / " in doc_texts
    assert any(m.level is Level.WARNING for m in messages.items)


# — Lieferschein ——————————————————————————————————————————————————————————————


def test_delivery_note(sample_settings, sample_data_root):
    args = create_document_args(
        DocumentKind.DELIVERY_NOTE, "1234", "4100012345", date(2025, 8, 22)
    )
    generate_document(args, date(2025, 8, 15), sample_settings)

    doc = open_document(sample_data_root, "Lieferschein Nr. 1234.docx")
    doc_texts = texts(doc)
    assert_items_and_sums(doc)
    assert_no_placeholders_left(doc)
    assert "Datum:\t15.08.2025" in doc_texts
    assert "Lieferschein Nr. 1234 – 4100012345" in doc_texts
    assert "Auftragsnummer:\t1234 / 4100012345" in doc_texts
    assert (
        "Vielen Dank für ihr Vertrauen in Heinrich Metallbau. "
        "Wir liefern folgende Positionen an: "
    ) in doc_texts
    assert "Liefertermin: 22.08.2025" in doc_texts


# — Rechnung und Auftragsbestätigung ——————————————————————————————————————————


@pytest.mark.parametrize(
    ("kind", "filename", "doctype", "header"),
    [
        (
            DocumentKind.INVOICE,
            "Rechnung Nr. 1234 - 4100012345.docx",
            "Rechnung",
            "Wir bitten um Ausgleich der folgenden Positionen:",
        ),
        (
            DocumentKind.ORDER_CONFIRMATION,
            "Auftragsbestätigung Nr. 1234 - 4100012345.docx",
            "Auftragsbestätigung",
            "Wir bestätigen den Auftrag über folgende Positionen:",
        ),
    ],
)
def test_invoice_and_order_confirmation(
    sample_settings, sample_data_root, kind, filename, doctype, header
):
    args = create_document_args(kind, "1234", "4100012345", date(2025, 8, 18))
    generate_document(args, date(2025, 8, 20), sample_settings)

    doc = open_document(sample_data_root, filename)
    doc_texts = texts(doc)
    assert_items_and_sums(doc)
    assert_no_placeholders_left(doc)
    assert "Datum:\t20.08.2025" in doc_texts
    assert f"{doctype} Nr. 1234 – 4100012345" in doc_texts
    assert "Auftragsnummer:\t1234 / 4100012345" in doc_texts
    assert (
        f"Vielen Dank für ihr Vertrauen in Heinrich Metallbau. {header} "
    ) in doc_texts
    assert "Liefertermin: 18.08.2025" in doc_texts


# — Errors ————————————————————————————————————————————————————————————————————


def test_csv_without_order_numbers_raises(sample_settings, sample_data_root):
    # No row has an order number; such rows are billed separately and skipped
    write_variant(sample_data_root / PROJECT_FOLDER, column="Auftrags-Nr.", value="")

    with pytest.raises(ValueError):
        args = create_document_args(DocumentKind.OFFER, "1234", None, date(2025, 8, 15))
        generate_document(args, date(2025, 8, 1), sample_settings)
