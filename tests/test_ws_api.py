"""Unit tests for the programme_tnt_fr websocket API handlers.

These tests call the raw handler functions directly with lightweight
stand-ins for hass/connection/msg (no real Home Assistant runtime, no
event loop) - the same "pure logic, no I/O" philosophy already used in
test_coordinator.py, since this repo has no pytest-homeassistant-custom-
component fixtures set up (see conftest.py, and .github/workflows/tests.yml,
which only installs plain `homeassistant` + `pytest`). The @callback and
@websocket_api.websocket_command decorators only attach metadata to these
functions - they don't change the calling convention - so calling them
directly with plain positional args exercises the real handler body.
"""
from unittest.mock import MagicMock

from custom_components.programme_tnt_fr.const import CONF_REMINDER_PROFILES, DOMAIN
from custom_components.programme_tnt_fr.ws_api import (
    websocket_get_programmes,
    websocket_get_reminder_profiles,
)


class _FakeCoordinator:
    def __init__(self, programmes_by_channel):
        self._programmes_by_channel = programmes_by_channel

    def get_programmes_for_day(self, channel_id, date_str):
        return self._programmes_by_channel.get(channel_id)


class _FakeConfigEntry:
    def __init__(self, options=None):
        self.options = options or {}


def _fake_connection():
    connection = MagicMock()
    connection.send_result = MagicMock()
    return connection


def test_websocket_get_programmes_merges_across_coordinators():
    # Two config entries (two coordinators) covering different channels -
    # the handler must merge results from all of them, not just the first.
    hass = MagicMock()
    hass.data = {
        DOMAIN: {
            "entry1": _FakeCoordinator({"tf1": [{"title": "JT"}]}),
            "entry2": _FakeCoordinator({"m6": [{"title": "Capital"}]}),
        }
    }
    connection = _fake_connection()
    msg = {"id": 42, "channels": ["tf1", "m6"], "date": "2026-09-06"}

    websocket_get_programmes(hass, connection, msg)

    connection.send_result.assert_called_once_with(
        42, {"programmes": {"tf1": [{"title": "JT"}], "m6": [{"title": "Capital"}]}}
    )


def test_websocket_get_programmes_skips_channel_with_no_data():
    # A channel_id with no cached programmes (coordinator returns None) is
    # simply omitted from the result, not included as an empty/None entry.
    hass = MagicMock()
    hass.data = {DOMAIN: {"entry1": _FakeCoordinator({"tf1": [{"title": "JT"}]})}}
    connection = _fake_connection()
    msg = {"id": 1, "channels": ["tf1", "unknown_channel"]}

    websocket_get_programmes(hass, connection, msg)

    connection.send_result.assert_called_once_with(
        1, {"programmes": {"tf1": [{"title": "JT"}]}}
    )


def test_websocket_get_programmes_no_coordinators_returns_empty():
    hass = MagicMock()
    hass.data = {}
    connection = _fake_connection()
    msg = {"id": 7, "channels": ["tf1"]}

    websocket_get_programmes(hass, connection, msg)

    connection.send_result.assert_called_once_with(7, {"programmes": {}})


def test_websocket_get_reminder_profiles_lists_names_across_entries():
    hass = MagicMock()
    hass.config_entries.async_entries.return_value = [
        _FakeConfigEntry({CONF_REMINDER_PROFILES: [{"name": "Fred"}, {"name": "Ginie"}]}),
    ]
    connection = _fake_connection()
    msg = {"id": 3}

    websocket_get_reminder_profiles(hass, connection, msg)

    connection.send_result.assert_called_once_with(3, {"profiles": ["Fred", "Ginie"]})


def test_websocket_get_reminder_profiles_deduplicates_names():
    # Two config entries both defining a profile with the same name should
    # not produce a duplicate in the result (matches the real
    # "if name and name not in names" guard).
    hass = MagicMock()
    hass.config_entries.async_entries.return_value = [
        _FakeConfigEntry({CONF_REMINDER_PROFILES: [{"name": "Fred"}]}),
        _FakeConfigEntry({CONF_REMINDER_PROFILES: [{"name": "Fred"}, {"name": "Ginie"}]}),
    ]
    connection = _fake_connection()
    msg = {"id": 4}

    websocket_get_reminder_profiles(hass, connection, msg)

    connection.send_result.assert_called_once_with(4, {"profiles": ["Fred", "Ginie"]})


def test_websocket_get_reminder_profiles_empty_when_none_configured():
    hass = MagicMock()
    hass.config_entries.async_entries.return_value = [_FakeConfigEntry()]
    connection = _fake_connection()
    msg = {"id": 5}

    websocket_get_reminder_profiles(hass, connection, msg)

    connection.send_result.assert_called_once_with(5, {"profiles": []})
