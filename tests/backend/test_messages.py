"""Tests for collecting user-facing messages by level."""

from heinrich_tool.backend.messages import Messages


def test_error_marks_messages_as_failed(messages: Messages):
    messages.info("Projektordner gefunden (1234 - Schutzgitter Mischer 3)")
    messages.error("PDF-Erzeugung fehlgeschlagen (Word nicht gefunden)")
    assert messages.has_errors


def test_info_and_warning_do_not_mark_messages_as_failed(messages: Messages):
    messages.info("Angebot erzeugt (Angebot Nr. 1234.docx)")
    messages.warning("Zeile 11 ohne Auftrags-Nr. übersprungen")
    assert not messages.has_errors
