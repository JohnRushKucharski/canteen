"""Tests for shared plugin utility helpers."""

import pytest

from canteen._plugin_utils import _is_file_plugins_disabled


@pytest.mark.parametrize("value", ["1", "true", "TRUE", "yes", "YeS"])
def test_is_file_plugins_disabled_true_values(
    monkeypatch: pytest.MonkeyPatch, value: str
) -> None:
    """Kill switch should disable file plugins for accepted true values."""
    monkeypatch.setenv("CANTEEN_DISABLE_FILE_PLUGINS", value)

    assert _is_file_plugins_disabled() is True


@pytest.mark.parametrize("value", ["0", "false", "no", "", "unexpected"])
def test_is_file_plugins_disabled_false_values(
    monkeypatch: pytest.MonkeyPatch, value: str
) -> None:
    """Kill switch should remain off for non-true values."""
    monkeypatch.setenv("CANTEEN_DISABLE_FILE_PLUGINS", value)

    assert _is_file_plugins_disabled() is False


def test_is_file_plugins_disabled_false_when_unset(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Kill switch defaults to off when the variable is missing."""
    monkeypatch.delenv("CANTEEN_DISABLE_FILE_PLUGINS", raising=False)

    assert _is_file_plugins_disabled() is False
