"""Tests for finding the project folder and its latest CSV."""

import os
from pathlib import Path

import pytest

from src.backend.paths import get_latest_csv_path, get_project_dir


def write_csv(project_dir: Path, name: str, mtime: int) -> Path:
    csv_path = project_dir / name
    csv_path.write_text("", encoding="utf-8")
    os.utime(csv_path, (mtime, mtime))
    return csv_path


# — Project folder ————————————————————————————————————————————————————————————


def test_project_folder_is_found_by_its_number(tmp_path):
    (tmp_path / "12345 - Abdeckblech Förderband").mkdir()
    (tmp_path / "1234 - Schutzgitter Mischer 3").mkdir()

    project_dir, _ = get_project_dir(tmp_path, "1234")

    assert project_dir == tmp_path / "1234 - Schutzgitter Mischer 3"


def test_file_with_the_project_number_is_not_a_project_folder(tmp_path):
    (tmp_path / "1234 - Aufmaß Schutzgitter.pdf").write_text("", encoding="utf-8")

    with pytest.raises(FileNotFoundError):
        get_project_dir(tmp_path, "1234")


def test_unknown_project_number_raises(tmp_path):
    (tmp_path / "1234 - Schutzgitter Mischer 3").mkdir()

    with pytest.raises(FileNotFoundError):
        get_project_dir(tmp_path, "4321")


# — Latest CSV ————————————————————————————————————————————————————————————————


def test_latest_csv_is_the_most_recently_modified(tmp_path, sample_config):
    write_csv(tmp_path, "heinrich_zeiterfassung_2025-08-01.csv", mtime=1_754_000_000)
    newest = write_csv(
        tmp_path, "heinrich_zeiterfassung_2025-07-01.csv", mtime=1_756_000_000
    )

    csv_path, _ = get_latest_csv_path(tmp_path, sample_config)

    assert csv_path == newest


def test_project_folder_without_csv_raises(tmp_path, sample_config):
    (tmp_path / "Angebot Nr. 1234.docx").write_text("", encoding="utf-8")

    with pytest.raises(FileNotFoundError):
        get_latest_csv_path(tmp_path, sample_config)
