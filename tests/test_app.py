"""UI tests for the Streamlit app."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import heinrich_tool
from heinrich_tool.backend import services
from heinrich_tool.backend.config import DocumentKind
from heinrich_tool.backend.input_args import DocumentArgs
from heinrich_tool.backend.messages import Messages
from heinrich_tool.backend.settings import Settings
from samples import SAMPLE_CONFIG_PATH, SAMPLE_TEMPLATE_PATH

APP_PATH = Path(heinrich_tool.__file__).parent / "app.py"


@pytest.fixture
def generated(monkeypatch, tmp_path) -> list[DocumentArgs]:
    """Arguments of every generation run; the real settings file is never read."""
    settings = Settings(
        data_root=tmp_path,
        config_path=SAMPLE_CONFIG_PATH,
        template_path=SAMPLE_TEMPLATE_PATH,
    )
    calls = []

    def fake_generate(args, document_date, settings):
        calls.append(args)
        return Messages()

    monkeypatch.setattr(services, "load_settings", lambda: settings)
    monkeypatch.setattr(services, "generate_document", fake_generate)
    return calls


@pytest.fixture
def app(generated) -> AppTest:
    return AppTest.from_file(str(APP_PATH)).run()


def fill_in(app: AppTest, project_number: str, receipt_number: str) -> None:
    app.text_input(key="project_number").input(project_number)
    app.text_input(key="receipt_number").input(receipt_number)


def click_generate(app: AppTest) -> None:
    next(b for b in app.button if b.label == "Erzeugen").click()
    app.run()


def test_inputs_stay_after_generating(app, generated):
    fill_in(app, "1234", "4100012345")
    click_generate(app)

    assert len(generated) == 1
    assert app.text_input(key="project_number").value == "1234"
    assert app.text_input(key="receipt_number").value == "4100012345"


def test_inputs_stay_when_switching_document(app, generated):
    fill_in(app, "1234", "4100012345")
    click_generate(app)
    app.selectbox(key="document_kind").select(DocumentKind.DELIVERY_NOTE)
    click_generate(app)

    assert [args.kind for args in generated] == [
        DocumentKind.OFFER,
        DocumentKind.DELIVERY_NOTE,
    ]
    assert app.text_input(key="project_number").value == "1234"
    assert app.text_input(key="receipt_number").value == "4100012345"
