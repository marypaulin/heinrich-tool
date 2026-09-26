"""
Word document generation.
"""

import logging
from collections.abc import Iterator
from copy import deepcopy
from pathlib import Path

from docx import Document
from docx.document import Document as DocxDocument  # Only for type hints
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.opc.exceptions import PackageNotFoundError
from docx.shared import Pt
from docx.table import _Cell, _Row
from docx.text.paragraph import Paragraph

from .formatting import format_price, format_quantity
from .models import LineItem
from .paths import VORDRUCK_PATH, get_display_path, get_intermediate_template_path


def load_template() -> DocxDocument:
    try:
        doc = Document(str(VORDRUCK_PATH))
        display_path = get_display_path(VORDRUCK_PATH)
        logging.info(f"Using template: {display_path}")
        return doc
    except PackageNotFoundError:
        raise ValueError(f"Template not found: {VORDRUCK_PATH}")


def save_docx(doc: DocxDocument, path: Path) -> None:
    doc.save(str(path))


def save_intermediate_template(project_number: str, doc: DocxDocument) -> None:
    path = get_intermediate_template_path(project_number)
    path.parent.mkdir(parents=True, exist_ok=True)
    save_docx(doc, path)


def load_intermediate_template(project_number: str) -> DocxDocument:
    path = get_intermediate_template_path(project_number)
    try:
        doc = Document(str(path))
        display_path = get_display_path(path)
        logging.info(f"Using intermediate template: {display_path}")
        return doc
    except PackageNotFoundError:
        raise ValueError(
            "Intermediate template not found - generate Angebot or Lieferschein first."
        )


def _body_and_table_paragraphs(doc: DocxDocument) -> Iterator[Paragraph]:
    yield from doc.paragraphs
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                yield from cell.paragraphs


def _replace_in_paragraph(paragraph: Paragraph, placeholder: str, value: str) -> None:
    """Replace every occurrence of a placeholder, even one split across runs.

    Word splits text into runs arbitrarily, e.g. "<Lieferdatum>" into "<",
    "Lieferdatum" and ">", so the texts of all runs are joined before
    searching for the placeholder. The value goes into the first run the
    placeholder touches and takes that run's formatting; the rest of the
    placeholder is removed from the following runs.
    """
    search_from = 0
    while True:
        runs = paragraph.runs
        start = "".join(run.text for run in runs).find(placeholder, search_from)
        if start == -1:
            return
        end = start + len(placeholder)
        run_start = 0
        value_inserted = False
        for run in runs:
            run_end = run_start + len(run.text)
            if run_start < end and run_end > start:
                before = run.text[: max(start - run_start, 0)]
                after = run.text[max(end - run_start, 0) :]
                run.text = before + ("" if value_inserted else value) + after
                value_inserted = True
            run_start = run_end
        # Continue after the inserted value: a value that contains the placeholder
        # itself would otherwise be found again and replaced forever.
        search_from = start + len(value)


def replace_placeholders(doc: DocxDocument, mapping: dict[str, str]) -> None:
    for paragraph in _body_and_table_paragraphs(doc):
        for placeholder, value in mapping.items():
            _replace_in_paragraph(paragraph, placeholder, value)


def _format_cell(
    cell: _Cell, font_name: str = "Calibri", font_size: int = 9, bold: bool = True
) -> None:
    for paragraph in cell.paragraphs:
        for run in paragraph.runs:
            run.font.name = font_name
            run.font.size = Pt(font_size)
            run.font.bold = bold


def _fill_row_cells(row: _Row, pos: int, item: LineItem) -> None:
    cells = row.cells
    cells[0].text = str(pos)
    cells[1].text = format_quantity(item.quantity)
    cells[2].text = item.description
    cells[3].text = format_price(item.unit_price)
    cells[4].text = format_price(item.total_price)
    for cell in cells:
        _format_cell(cell)
    cells[3].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
    cells[4].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT


def fill_table_with_line_items(doc: DocxDocument, line_items: list[LineItem]) -> None:
    """Fill the line item table, recognized by five columns and the header "Pos".

    The template holds one empty row below the header. The first item goes
    there; each further item gets a copy of that row, inserted after the
    previous item so the sum rows stay below.
    """
    for table in doc.tables:
        if len(table.columns) == 5 and table.cell(0, 0).text == "Pos":
            first_row = table.rows[1]
            _fill_row_cells(first_row, pos=1, item=line_items[0])
            previous_tr = first_row._tr
            for pos, item in enumerate(line_items[1:], start=2):
                tr = deepcopy(first_row._tr)
                previous_tr.addnext(tr)
                _fill_row_cells(_Row(tr, table), pos=pos, item=item)
                previous_tr = tr
            return

    raise ValueError("No matching table found in template document.")
