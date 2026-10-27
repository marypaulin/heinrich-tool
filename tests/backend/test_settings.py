"""Tests for the machine-local settings file."""

import pytest

from heinrich_tool.backend.settings import Settings, read_settings, write_settings


def test_saved_settings_are_loaded(tmp_path):
    settings_path = tmp_path / "HeinrichTool" / "settings.json"
    settings = Settings(
        data_root=tmp_path / "Daten",
        config_path=tmp_path / "Daten" / "Tool" / "config.json",
        template_path=tmp_path / "Daten" / "Tool" / "Vordruck.docx",
    )

    write_settings(settings_path, settings)

    assert read_settings(settings_path) == settings


def test_missing_settings_file_gives_none(tmp_path):
    assert read_settings(tmp_path / "settings.json") is None


def test_broken_settings_file_raises(tmp_path):
    settings_path = tmp_path / "settings.json"
    settings_path.write_text("{", encoding="utf-8")

    with pytest.raises(ValueError):
        read_settings(settings_path)
