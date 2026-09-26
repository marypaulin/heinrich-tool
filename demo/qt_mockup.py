"""Qt-Entwurf der geplanten Oberfläche — reines Frontend, keine Backend-Logik."""

import sys
import tempfile
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from PySide6.QtCore import QAbstractTableModel, QDate, QModelIndex, QPointF, Qt
from PySide6.QtGui import QColor, QFont, QImage, QPainter, QPalette, QPen, QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QComboBox,
    QDateEdit,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QStackedWidget,
    QStyledItemDelegate,
    QTableView,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"

# Dokumenttyp -> (Belegnummer-Regel, Liefertermin-Vorbelegung in Tagen)
DOC_TYPES = {
    "Angebot": ("keine", 21),
    "Lieferschein": ("optional", 0),
    "Rechnung": ("pflicht", 0),
    "Auftragsbestätigung": ("pflicht", 0),
}

# — Farbwelt ———————————————————————————————————————————————————————————————————

BG_APP = "#0b1220"
BG_SIDEBAR = "#0d1524"
BG_CARD = "#141d30"
BG_INPUT = "#0f1829"
BG_ELEVATED = "#1a2438"
BORDER = "#26324a"
BORDER_SOFT = "#1b2436"
TEXT = "#e7edf9"
TEXT_DIM = "#94a3b8"
TEXT_MUTE = "#64748b"
BLUE = "#60a5fa"
GREEN = "#4ade80"
PURPLE = "#a78bfa"
SELECTION = "#1d3557"

FONT_STACK = '"Segoe UI", "Inter", "Noto Sans", "DejaVu Sans", sans-serif'


def _stylesheet(icons: dict[str, str]) -> str:
    return f"""
* {{
    font-family: {FONT_STACK};
    font-size: 14px;
    color: {TEXT};
}}

QMainWindow, QWidget#Page {{ background: {BG_APP}; }}
QWidget#Row, QWidget#Form {{ background: transparent; }}
QStatusBar {{ background: {BG_SIDEBAR}; color: {TEXT_MUTE}; border-top: 1px solid {BORDER_SOFT}; }}
QToolTip {{ background: {BG_ELEVATED}; color: {TEXT}; border: 1px solid {BORDER};
            border-radius: 6px; padding: 6px 8px; }}

/* — Seitenleiste — */
QListWidget#Sidebar {{
    background: {BG_SIDEBAR};
    border: none;
    border-right: 1px solid {BORDER_SOFT};
    outline: 0;
    padding: 10px 10px;
}}
QListWidget#Sidebar::item {{
    padding: 11px 14px;
    border-radius: 10px;
    color: {TEXT_DIM};
    margin-bottom: 4px;
}}
QListWidget#Sidebar::item:hover {{ background: {BG_CARD}; color: {TEXT}; }}
QListWidget#Sidebar::item:selected {{
    background: rgba(96, 165, 250, 0.14);
    color: {BLUE};
    font-weight: 600;
}}

/* — Typografie — */
#Title {{ font-size: 30px; font-weight: 700; letter-spacing: -0.5px; }}
#Subtitle {{ color: {TEXT_DIM}; font-size: 14px; }}
#SectionLabel {{ font-size: 17px; font-weight: 600; }}
#Hint {{ color: {TEXT_MUTE}; font-size: 12.5px; }}
#Badge {{
    background: rgba(167, 139, 250, 0.15);
    color: {PURPLE};
    border: 1px solid rgba(167, 139, 250, 0.28);
    border-radius: 11px;
    padding: 3px 11px;
    font-size: 12px;
    font-weight: 600;
}}
#Total {{ font-size: 15px; font-weight: 600; color: {GREEN}; }}

/* — Karten — */
#Card {{
    background: {BG_CARD};
    border: 1px solid {BORDER_SOFT};
    border-radius: 16px;
}}
QLabel {{ background: transparent; }}

/* — Schaltflächen — */
QPushButton {{
    background: {BG_ELEVATED};
    color: {TEXT_DIM};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 10px 18px;
    font-weight: 600;
}}
QPushButton:hover {{ background: #22304a; color: {TEXT}; }}
QPushButton:pressed {{ background: #1a2438; }}
QPushButton:disabled {{ background: {BG_INPUT}; color: {TEXT_MUTE}; border-color: {BORDER_SOFT}; }}

QPushButton[accent="primary"] {{
    background: rgba(74, 222, 128, 0.16);
    color: {GREEN};
    border: 1px solid rgba(74, 222, 128, 0.32);
}}
QPushButton[accent="primary"]:hover {{ background: rgba(74, 222, 128, 0.24); }}
QPushButton[accent="primary"]:pressed {{ background: rgba(74, 222, 128, 0.12); }}

QPushButton[accent="blue"] {{
    background: rgba(96, 165, 250, 0.16);
    color: {BLUE};
    border: 1px solid rgba(96, 165, 250, 0.32);
}}
QPushButton[accent="blue"]:hover {{ background: rgba(96, 165, 250, 0.24); }}
QPushButton[accent="blue"]:pressed {{ background: rgba(96, 165, 250, 0.12); }}

/* — Eingabefelder — */
QLineEdit, QComboBox, QSpinBox, QDateEdit, QPlainTextEdit {{
    background: {BG_INPUT};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 9px 12px;
    selection-background-color: rgba(96, 165, 250, 0.35);
    selection-color: {TEXT};
}}
QLineEdit:hover, QComboBox:hover, QSpinBox:hover, QDateEdit:hover {{ border-color: #33415c; }}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDateEdit:focus, QPlainTextEdit:focus {{
    border-color: {BLUE};
    background: #101c33;
}}
QLineEdit:disabled, QComboBox:disabled, QSpinBox:disabled {{
    background: #0c1424;
    color: {TEXT_MUTE};
    border-color: {BORDER_SOFT};
}}
QLineEdit:read-only {{ background: #0c1424; color: {TEXT_DIM}; }}
QLineEdit[placeholderText] {{ color: {TEXT}; }}
QPlainTextEdit {{ padding: 12px; color: {TEXT_DIM}; }}

QComboBox::drop-down, QDateEdit::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: center right;
    border: none;
    background: transparent;
    width: 26px;
}}
QComboBox::down-arrow, QDateEdit::down-arrow {{
    image: url({icons["down"]});
    width: 13px;
    height: 13px;
}}
QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
    subcontrol-origin: border;
    border: none;
    background: transparent;
    width: 24px;
    height: 14px;
    padding-right: 6px;
}}
QSpinBox::up-button, QDoubleSpinBox::up-button {{
    subcontrol-position: top right;
    padding-top: 5px;
}}
QSpinBox::down-button, QDoubleSpinBox::down-button {{
    subcontrol-position: bottom right;
    padding-bottom: 5px;
}}
QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {{
    image: url({icons["up"]});
    width: 11px;
    height: 11px;
}}
QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {{
    image: url({icons["down"]});
    width: 11px;
    height: 11px;
}}
QComboBox QAbstractItemView {{
    background: {BG_ELEVATED};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 4px;
    outline: 0;
    selection-background-color: rgba(96, 165, 250, 0.18);
    selection-color: {BLUE};
}}

/* — Tabellen — */
QTableView {{
    background: {BG_CARD};
    alternate-background-color: #162035;
    border: 1px solid {BORDER_SOFT};
    border-radius: 14px;
    gridline-color: transparent;
    outline: 0;
}}
QTableView::item {{ padding: 0px 10px; border: none; color: {TEXT_DIM}; }}
QTableView::item:selected {{ background: rgba(96, 165, 250, 0.16); color: {TEXT}; }}
QHeaderView {{ background: transparent; }}
QHeaderView::section {{
    background: {BG_INPUT};
    color: {TEXT_MUTE};
    border: none;
    border-bottom: 1px solid {BORDER};
    padding: 11px 10px;
    font-weight: 600;
    font-size: 12.5px;
}}
QTableCornerButton::section {{ background: {BG_INPUT}; border: none; }}
QTableView QLineEdit, QTableView QDoubleSpinBox, QTableView QDateEdit {{
    padding: 1px 8px;
    border: 1px solid {BLUE};
    border-radius: 7px;
    background: {BG_ELEVATED};
    color: {TEXT};
}}
QTableView QDoubleSpinBox::up-button, QTableView QDoubleSpinBox::down-button {{
    width: 18px;
    padding-right: 4px;
}}

/* — Bildlaufleisten — */
QScrollBar:vertical {{ background: transparent; width: 10px; margin: 4px; }}
QScrollBar::handle:vertical {{ background: #2b3a55; border-radius: 5px; min-height: 30px; }}
QScrollBar::handle:vertical:hover {{ background: #3a4c6d; }}
QScrollBar:horizontal {{ background: transparent; height: 10px; margin: 4px; }}
QScrollBar::handle:horizontal {{ background: #2b3a55; border-radius: 5px; min-width: 30px; }}
QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; width: 0; }}
QScrollBar::add-page, QScrollBar::sub-page {{ background: transparent; }}

/* — Kalender im Datumsfeld — */
QCalendarWidget QWidget {{ background: {BG_ELEVATED}; }}
QCalendarWidget QAbstractItemView {{
    background: {BG_ELEVATED};
    selection-background-color: rgba(96, 165, 250, 0.25);
    selection-color: {TEXT};
    outline: 0;
}}
QCalendarWidget QToolButton {{ background: transparent; border: none; padding: 6px; }}
QCalendarWidget QToolButton:hover {{ background: {BG_CARD}; border-radius: 6px; }}
"""


DEMO_TIMESHEET = [
    [date(2025, 8, 1), "30014277", "Geländer montiert", 8.0, 62.50, 0.00],
    [date(2025, 8, 2), "30014277", "Materialkauf Stahl", 0.0, 62.50, 212.40],
    [date(2025, 8, 4), "30014277", "Schweißarbeiten", 6.5, 62.50, 0.00],
    [date(2025, 8, 5), "123", "Notiz ohne Auftrag", 2.0, 62.50, 0.00],
    [date(2025, 8, 7), "30014277", "Endmontage", 4.0, 78.00, 48.90],
]

DEMO_HOURS = [
    ("1408", "01.08.2025", "30014277", "Meisterstunde", "8,0", "62,50 €", "500,00 €"),
    ("1408", "04.08.2025", "30014277", "Meisterstunde", "6,5", "62,50 €", "406,25 €"),
    ("1408", "07.08.2025", "30014277", "Meisterstunde", "4,0", "78,00 €", "312,00 €"),
    ("1409", "12.08.2025", "30015034", "Helferstunde", "7,5", "39,00 €", "292,50 €"),
    ("1421", "09.09.2025", "30016185", "Meisterstunde", "9,0", "62,50 €", "562,50 €"),
]


# — Datenmodell der Zeiterfassung ——————————————————————————————————————————————


@dataclass(frozen=True)
class Column:
    title: str
    kind: str
    editable: bool = True


TIMESHEET_COLUMNS = (
    Column("Datum", "date"),
    Column("Auftrags-Nr.", "text"),
    Column("Beschreibung", "text"),
    Column("Dauer (Std)", "hours"),
    Column("Stundensatz (€)", "money"),
    Column("Material (€)", "money"),
    Column("Gesamtkosten (€)", "money", editable=False),
)

TOTAL_COLUMN = len(TIMESHEET_COLUMNS) - 1


def _german_number(value: float, decimals: int) -> str:
    return (
        f"{value:,.{decimals}f}".replace(",", "\u00a0")
        .replace(".", ",")
        .replace("\u00a0", ".")
    )


class TimesheetModel(QAbstractTableModel):
    """Hält die CSV-Zeilen als native Werte — Datum als `date`, Beträge als `float`.

    Die Gesamtkosten stehen nicht in den Daten, sondern werden bei jedem Zugriff
    gerechnet; dadurch kann die Spalte nach einer Änderung nicht veralten.
    """

    def __init__(self, rows: list[list]):
        super().__init__()
        self._rows = [list(row) for row in rows]

    def rowCount(self, parent=QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self._rows)

    def columnCount(self, parent=QModelIndex()) -> int:
        return 0 if parent.isValid() else len(TIMESHEET_COLUMNS)

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if (
            orientation == Qt.Orientation.Horizontal
            and role == Qt.ItemDataRole.DisplayRole
        ):
            return TIMESHEET_COLUMNS[section].title
        return None

    def flags(self, index):
        flags = super().flags(index)
        if TIMESHEET_COLUMNS[index.column()].editable:
            flags |= Qt.ItemFlag.ItemIsEditable
        return flags

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        value = self._value(index.row(), index.column())
        if role == Qt.ItemDataRole.EditRole:
            return value
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        kind = TIMESHEET_COLUMNS[index.column()].kind
        if kind == "date":
            return value.strftime("%d.%m.%Y")
        if kind == "hours":
            return _german_number(value, 1)
        if kind == "money":
            return _german_number(value, 2)
        return value

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole) -> bool:
        if role != Qt.ItemDataRole.EditRole:
            return False
        if not TIMESHEET_COLUMNS[index.column()].editable:
            return False
        self._rows[index.row()][index.column()] = value
        self.dataChanged.emit(index, index)
        total = self.index(index.row(), TOTAL_COLUMN)
        self.dataChanged.emit(total, total)
        return True

    def _value(self, row: int, column: int):
        values = self._rows[row]
        if column == TOTAL_COLUMN:
            _, _, _, hours, rate, material = values
            return hours * rate + material
        return values[column]


class TimesheetDelegate(QStyledItemDelegate):
    """Der Editor gehört zur Spalte, nicht zum Zufall — Datumsfeld, Zahlenfeld oder Text.

    `updateEditorGeometry` ist nötig, weil der Editor sonst den Innenabstand der Zelle
    erbt und auf wenige Pixel Texthöhe zusammenfällt.
    """

    def createEditor(self, parent, option, index):
        kind = TIMESHEET_COLUMNS[index.column()].kind
        if kind == "date":
            editor = QDateEdit(parent, calendarPopup=True)
            editor.setDisplayFormat("dd.MM.yyyy")
            return editor
        if kind in ("hours", "money"):
            editor = QDoubleSpinBox(parent)
            editor.setDecimals(1 if kind == "hours" else 2)
            editor.setMaximum(1_000_000)
            editor.setGroupSeparatorShown(kind == "money")
            return editor
        return QLineEdit(parent)

    def setEditorData(self, editor, index):
        value = index.data(Qt.ItemDataRole.EditRole)
        if isinstance(editor, QDateEdit):
            editor.setDate(QDate(value.year, value.month, value.day))
        elif isinstance(editor, QDoubleSpinBox):
            editor.setValue(value)
        else:
            editor.setText(str(value))

    def setModelData(self, editor, model, index):
        if isinstance(editor, QDateEdit):
            model.setData(index, editor.date().toPython())
        elif isinstance(editor, QDoubleSpinBox):
            model.setData(index, editor.value())
        else:
            model.setData(index, editor.text())

    def updateEditorGeometry(self, editor, option, index):
        rect = option.rect.adjusted(2, 4, -2, -4)
        rect.setWidth(max(rect.width(), editor.sizeHint().width()))
        editor.setGeometry(rect)


# — Symbole ————————————————————————————————————————————————————————————————————


def _chevrons(color: str, size: int = 26) -> dict[str, str]:
    """Qt-Stylesheets brauchen für Pfeile eine Bilddatei — hier zur Laufzeit gezeichnet,
    damit weder Binärdateien im Repo noch das Qt-Ressourcensystem nötig sind."""
    directory = Path(tempfile.mkdtemp(prefix="heinrich-icons-"))
    icons = {}
    for name, sign in (("down", 1), ("up", -1)):
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor(color), size * 0.11)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        mid, arm = size / 2, size * 0.21
        painter.drawPolyline(
            [
                QPointF(mid - arm * 1.5, mid - arm * sign * 0.7),
                QPointF(mid, mid + arm * sign * 0.7),
                QPointF(mid + arm * 1.5, mid - arm * sign * 0.7),
            ]
        )
        painter.end()
        path = directory / f"chevron-{name}.png"
        pixmap.save(str(path))
        icons[name] = path.as_posix()
    return icons


def _light_logo(path: Path, height: int) -> QPixmap:
    """Das Firmenlogo ist schwarz auf transparent und auf dunklem Grund unlesbar."""
    image = QImage(str(path)).convertToFormat(QImage.Format.Format_ARGB32)
    image.invertPixels(QImage.InvertMode.InvertRgb)
    return QPixmap.fromImage(image).scaledToHeight(
        height, Qt.TransformationMode.SmoothTransformation
    )


# — Hilfsfunktionen ————————————————————————————————————————————————————————————


def _apply_shadow(widget: QWidget, blur: int = 28, alpha: int = 110, dy: int = 6):
    """Qt-Stylesheets kennen kein box-shadow; Tiefe geht nur über einen Grafikeffekt."""
    effect = QGraphicsDropShadowEffect(widget)
    effect.setBlurRadius(blur)
    effect.setOffset(0, dy)
    effect.setColor(QColor(0, 0, 0, alpha))
    widget.setGraphicsEffect(effect)


def _row(*widgets: QWidget, stretch: bool = False, spacing: int = 10) -> QWidget:
    """Waagerechter Container ohne eigenen Hintergrund."""
    container = QWidget()
    container.setObjectName("Row")
    layout = QHBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(spacing)
    for widget in widgets:
        layout.addWidget(widget)
    if stretch:
        layout.addStretch()
    return container


def _card(*widgets: QWidget) -> QFrame:
    """Umrandeter Block, entspricht den Formularkästen der Streamlit-Version."""
    frame = QFrame()
    frame.setObjectName("Card")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(24, 24, 24, 24)
    layout.setSpacing(16)
    for widget in widgets:
        layout.addWidget(widget)
    _apply_shadow(frame)
    return frame


def _button(text: str, accent: str = "") -> QPushButton:
    """`accent` als dynamische Eigenschaft — das Stylesheet greift per Attributselektor."""
    button = QPushButton(text)
    if accent:
        button.setProperty("accent", accent)
    return button


def _section(text: str) -> QLabel:
    label = QLabel(text)
    label.setObjectName("SectionLabel")
    return label


def _hint(text: str) -> QLabel:
    label = QLabel(text)
    label.setObjectName("Hint")
    label.setWordWrap(True)
    return label


def _form(rows: list[tuple[str, QWidget]]) -> QWidget:
    form = QWidget()
    form.setObjectName("Form")
    layout = QFormLayout(form)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setHorizontalSpacing(20)
    layout.setVerticalSpacing(14)
    layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
    for text, widget in rows:
        label = QLabel(text)
        label.setStyleSheet(f"color: {TEXT_DIM}; font-weight: 600;")
        layout.addRow(label, widget)
    return form


def _configure_table(view: QAbstractItemView, stretch_column: int):
    """`stretch_column` bekommt den Überschuss; alle übrigen Spalten richten sich nach
    ihrem Inhalt, sonst schneidet Qt die längste Überschrift ab."""
    view.verticalHeader().setVisible(False)
    view.setAlternatingRowColors(True)
    view.setShowGrid(False)
    view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    header = view.horizontalHeader()
    header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
    header.setSectionResizeMode(stretch_column, QHeaderView.ResizeMode.Stretch)
    header.setHighlightSections(False)
    header.setMinimumSectionSize(90)
    header.setDefaultAlignment(
        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
    )
    view.verticalHeader().setDefaultSectionSize(40)


def _table(headers: list[str], rows: list[tuple], stretch_column: int) -> QTableWidget:
    """Nur-Lese-Tabelle für vorformatierte Zeilen."""
    table = QTableWidget(len(rows), len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    _configure_table(table, stretch_column)
    for r, row in enumerate(rows):
        for c, value in enumerate(row):
            item = QTableWidgetItem(value)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            table.setItem(r, c, item)
    return table


def _editable_table(model: QAbstractTableModel, stretch_column: int) -> QTableView:
    view = QTableView()
    view.setModel(model)
    view.setItemDelegate(TimesheetDelegate(view))
    _configure_table(view, stretch_column)
    return view


# — Seite: Dokumente ———————————————————————————————————————————————————————————


class DocumentsPage(QWidget):
    def __init__(self):
        super().__init__()

        self.doc_type = QComboBox()
        self.doc_type.addItems(DOC_TYPES.keys())
        self.doc_type.currentTextChanged.connect(self._on_doc_type_changed)

        self.project_number = QLineEdit(placeholderText="z. B. 1408")
        self.receipt_number = QLineEdit(placeholderText="z. B. 8100045372")

        self.delivery_days = QSpinBox(minimum=0, maximum=365, suffix=" Tage")
        self.delivery_days.setMinimumWidth(120)
        self.delivery_days.valueChanged.connect(self._on_days_changed)

        self.delivery_date = QDateEdit(calendarPopup=True)
        self.delivery_date.setDisplayFormat("dd.MM.yyyy")
        self.delivery_date.setMinimumWidth(140)
        self.delivery_date.dateChanged.connect(self._on_date_changed)

        entspricht = QLabel("entspricht")
        entspricht.setObjectName("Hint")
        delivery_row = _row(
            self.delivery_days, entspricht, self.delivery_date, stretch=True
        )

        form = _form(
            [
                ("Dokumenttyp", self.doc_type),
                ("Projektnummer", self.project_number),
                ("Belegnummer", self.receipt_number),
                ("Liefertermin", delivery_row),
            ]
        )

        self.generate_button = _button("Dokument erzeugen", accent="primary")
        self.generate_button.clicked.connect(self._on_generate)
        button_row = _row(self.generate_button, _button("Zurücksetzen"), stretch=True)

        self.output = QPlainTextEdit(readOnly=True)
        self.output.setFont(QFont("monospace", 10))
        self.output.setMinimumHeight(170)
        self.output.setPlainText("Noch kein Dokument erzeugt.")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        card = _card(form, button_row)
        card.setMaximumWidth(760)

        layout.addWidget(_section("Dokument erzeugen"))
        layout.addWidget(card)
        layout.addWidget(_section("Verlauf"))
        layout.addWidget(self.output)

        self._on_doc_type_changed(self.doc_type.currentText())

    def _on_doc_type_changed(self, doc_type: str):
        rule, default_days = DOC_TYPES[doc_type]
        self.receipt_number.setEnabled(rule != "keine")
        if rule == "keine":
            self.receipt_number.clear()
            self.receipt_number.setPlaceholderText("für Angebot nicht erforderlich")
        elif rule == "optional":
            self.receipt_number.setPlaceholderText("optional — z. B. 8100045372")
        else:
            self.receipt_number.setPlaceholderText("erforderlich — z. B. 8100045372")
        self.delivery_days.setValue(default_days)

    def _on_days_changed(self, days: int):
        self.delivery_date.blockSignals(True)
        self.delivery_date.setDate(QDate.currentDate().addDays(days))
        self.delivery_date.blockSignals(False)

    def _on_date_changed(self, value: QDate):
        self.delivery_days.blockSignals(True)
        self.delivery_days.setValue(max(0, QDate.currentDate().daysTo(value)))
        self.delivery_days.blockSignals(False)

    def _on_generate(self):
        doc_type = self.doc_type.currentText()
        project = self.project_number.text().strip() or "1408"
        self.output.setPlainText(
            "\n".join(
                [
                    f"Projektordner gefunden: Datenordner/{project} - Allgemein Juli",
                    "CSV Datei gefunden: heinrich_zeiterfassung_2025-08-01.csv",
                    "Achtung: Überspringe Zeile 4 mit ungültiger Auftrags-Nr. 123",
                    f"{doc_type} erzeugt: {doc_type} Nr. {project}.docx",
                    f"PDF erzeugt: {doc_type} Nr. {project}.pdf",
                ]
            )
        )


# — Seite: Zeiterfassung ———————————————————————————————————————————————————————


class TimesheetPage(QWidget):
    """`editable=False` zeigt die Zeiterfassung nur an — der Stand vor dem CSV-Editor."""

    def __init__(self, editable: bool = True):
        super().__init__()

        self.model = TimesheetModel(DEMO_TIMESHEET)
        table = _editable_table(self.model, stretch_column=2)
        if not editable:
            table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        file_label = QLabel("Datei")
        file_label.setStyleSheet(f"color: {TEXT_DIM}; font-weight: 600;")
        path_row = _row(
            file_label,
            QLineEdit("heinrich_zeiterfassung_2025-08-01.csv", readOnly=True),
            _button("Andere Datei…", accent="blue"),
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        layout.addWidget(
            _section("Zeiterfassung bearbeiten" if editable else "Zeiterfassung")
        )
        layout.addWidget(path_row)
        layout.addWidget(table)

        if editable:
            layout.addWidget(
                _hint(
                    "Doppelklick bearbeitet eine Zelle — Datum, Zahl oder Text je nach "
                    "Spalte, die Gesamtkosten rechnen sich mit. Änderungen werden in "
                    "dieselbe Datei zurückgeschrieben, im ursprünglichen Format."
                )
            )
            layout.addWidget(
                _row(
                    _button("Änderungen speichern", accent="primary"),
                    _button("Verwerfen"),
                    stretch=True,
                )
            )
        else:
            layout.addWidget(
                _hint(
                    "Zeigt die eingelesene Zeiterfassung des Projekts. Grundlage für "
                    "die Dokumente auf der nächsten Seite."
                )
            )


# — Seite: Stunden —————————————————————————————————————————————————————————————


class HoursPage(QWidget):
    def __init__(self):
        super().__init__()

        headers = [
            "Projekt",
            "Datum",
            "Auftrags-Nr.",
            "Art",
            "Stunden",
            "Satz",
            "Betrag",
        ]
        table = _table(headers, DEMO_HOURS, stretch_column=3)

        total = QLabel("Gesamt: 35,0 Stunden · 2.073,25 €")
        total.setObjectName("Total")

        button_row = _row(
            _button("Als CSV exportieren", accent="primary"), stretch=True
        )
        button_row.layout().addWidget(total)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        layout.addWidget(_section("Stundenarchiv"))
        layout.addWidget(table)
        layout.addWidget(
            _hint(
                "Wird bei jedem Öffnen neu aus den Projektordnern berechnet und ist "
                "damit immer aktuell."
            )
        )
        layout.addWidget(button_row)


# — Seite: Einstellungen ———————————————————————————————————————————————————————


class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()

        self.data_root = QLineEdit(
            "C:\\Users\\max\\OneDrive\\Datenordner", readOnly=True
        )
        browse = _button("Ordner wählen…", accent="blue")
        browse.clicked.connect(self._on_browse)

        form = _form(
            [
                ("Datenordner", _row(self.data_root, browse)),
                (
                    "Konfiguration",
                    QLineEdit("Datenordner/heinrich_config.json", readOnly=True),
                ),
                ("Word-Vorlage", QLineEdit("Datenordner/Vordruck.docx", readOnly=True)),
            ]
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        card = _card(form)
        card.setMaximumWidth(760)

        layout.addWidget(_section("Einstellungen"))
        layout.addWidget(card)
        layout.addWidget(
            _hint(
                "Nur der Datenordner wird auf diesem Rechner gespeichert. Konfiguration "
                "und Word-Vorlage liegen im Datenordner selbst und stehen dadurch über "
                "OneDrive auf allen Rechnern zur Verfügung. Die Konfiguration wird im "
                "Texteditor bearbeitet."
            )
        )
        layout.addStretch()

    def _on_browse(self):
        chosen = QFileDialog.getExistingDirectory(self, "Datenordner wählen")
        if chosen:
            self.data_root.setText(chosen)


# — Hauptfenster ———————————————————————————————————————————————————————————————


def _dark_palette() -> QPalette:
    """Popups, Dialoge und Textcursor zieht Fusion aus der Palette, nicht aus dem Stylesheet."""
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(BG_APP))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(TEXT))
    palette.setColor(QPalette.ColorRole.Base, QColor(BG_INPUT))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(BG_CARD))
    palette.setColor(QPalette.ColorRole.Text, QColor(TEXT))
    palette.setColor(QPalette.ColorRole.Button, QColor(BG_ELEVATED))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(TEXT))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(BG_ELEVATED))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(TEXT))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(SELECTION))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(TEXT))
    palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(TEXT_MUTE))
    palette.setColor(
        QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(TEXT_MUTE)
    )
    palette.setColor(
        QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(TEXT_MUTE)
    )
    return palette


class MainWindow(QMainWindow):
    def __init__(self, timesheet_editable: bool = True):
        super().__init__()
        self.setWindowTitle("Heinrich App")
        self.resize(1120, 760)

        title = QLabel("Projektabrechnung")
        title.setObjectName("Title")

        badge = QLabel("Entwurf")
        badge.setObjectName("Badge")

        subtitle = QLabel(
            "Angebote, Lieferscheine, Rechnungen und Auftragsbestätigungen "
            "direkt aus den Zeiterfassungsdaten."
        )
        subtitle.setObjectName("Subtitle")

        text_column = QVBoxLayout()
        text_column.setSpacing(6)
        text_column.addWidget(_row(title, badge, stretch=True, spacing=12))
        text_column.addWidget(subtitle)

        logo = QLabel()
        logo_path = ASSETS_DIR / "logo.png"
        if logo_path.exists():
            logo.setPixmap(_light_logo(logo_path, 46))

        header = QWidget()
        header.setObjectName("Page")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(36, 30, 36, 20)
        header_layout.addLayout(text_column)
        header_layout.addStretch()
        header_layout.addWidget(logo)

        self.nav = QListWidget()
        self.nav.setObjectName("Sidebar")
        self.nav.addItems(
            ["Zeiterfassung", "Dokumente", "Stundenarchiv", "Einstellungen"]
        )
        self.nav.setFixedWidth(200)
        self.nav.setCurrentRow(0)

        self.pages = QStackedWidget()
        pages = (
            TimesheetPage(timesheet_editable),
            DocumentsPage(),
            HoursPage(),
            SettingsPage(),
        )
        for page in pages:
            container = QWidget()
            container.setObjectName("Page")
            container_layout = QVBoxLayout(container)
            container_layout.setContentsMargins(36, 8, 36, 28)
            container_layout.addWidget(page)
            self.pages.addWidget(container)
        self.nav.currentRowChanged.connect(self.pages.setCurrentIndex)

        body = QWidget()
        body.setObjectName("Page")
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)
        body_layout.addWidget(self.nav)
        body_layout.addWidget(self.pages)

        central = QWidget()
        central.setObjectName("Page")
        central_layout = QVBoxLayout(central)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)
        central_layout.addWidget(header)
        central_layout.addWidget(body)
        self.setCentralWidget(central)

        self.statusBar().setSizeGripEnabled(False)
        self.statusBar().showMessage("Entwurf — ohne Backend-Logik")


# — Einstieg ———————————————————————————————————————————————————————————————————


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setPalette(_dark_palette())
    app.setStyleSheet(_stylesheet(_chevrons(TEXT_DIM)))
    window = MainWindow()

    if "--screenshot" in sys.argv:
        target = sys.argv[sys.argv.index("--screenshot") + 1]
        page = (
            int(sys.argv[sys.argv.index("--page") + 1]) if "--page" in sys.argv else 0
        )
        window.nav.setCurrentRow(page)
        window.show()
        app.processEvents()
        window.grab().save(target)
        print(f"gespeichert: {target}")
        return

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
