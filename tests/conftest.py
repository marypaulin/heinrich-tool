"""Shared test data: the sample config and an empty message collector."""

import pytest

from heinrich_tool.backend.config import Config, load_config
from heinrich_tool.backend.messages import Messages
from samples import SAMPLE_CONFIG_PATH


@pytest.fixture
def sample_config() -> Config:
    """Tests that need other values derive them with `dataclasses.replace`."""
    return load_config(SAMPLE_CONFIG_PATH)


@pytest.fixture
def messages() -> Messages:
    return Messages()
