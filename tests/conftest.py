"""Shared test data: the sample config every module test starts from."""

from pathlib import Path

import pytest

from src.backend.config import Config, load_config

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_CONFIG_PATH = FIXTURES_DIR / "config_sample.json"


@pytest.fixture
def sample_config() -> Config:
    """Tests that need other values derive them with `dataclasses.replace`."""
    return load_config(SAMPLE_CONFIG_PATH)
