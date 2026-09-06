"""Unit tests for the pure helper functions in config_flow.py.

Same philosophy as test_coordinator.py: no Home Assistant runtime, no
event loop - hass is a lightweight MagicMock exposing only the attributes
these two functions actually read (the notify services registry / the
entity registry), since this repo has no pytest-homeassistant-custom-
component fixtures set up (see conftest.py and .github/workflows/tests.yml,
which only installs plain `homeassistant` + `pytest`).
"""
from unittest.mock import MagicMock, patch

from custom_components.programme_tnt_fr.config_flow import (
    _notify_media_player_conflict,
    _notify_options,
)


def test_notify_options_excludes_generic_and_entity_based_services():
    hass = MagicMock()
    hass.services.async_services.return_value = {
        "notify": {
            "mobile_app_iphone_fred": None,
            "alexa_media_echo_salon": None,
            "send_message": None,
            "notify": None,
            "persistent_notification": None,
        }
    }

    options = _notify_options(hass)

    values = {opt["value"] for opt in options}
    assert values == {"mobile_app_iphone_fred", "alexa_media_echo_salon"}


def test_notify_options_empty_when_no_notify_domain():
    hass = MagicMock()
    hass.services.async_services.return_value = {}

    assert _notify_options(hass) == []


def _fake_entity_entry(platform):
    entry = MagicMock()
    entry.platform = platform
    return entry


def test_notify_media_player_conflict_true_for_same_alexa_device():
    hass = MagicMock()
    with patch("custom_components.programme_tnt_fr.config_flow.er.async_get") as async_get:
        registry = MagicMock()
        registry.async_get.return_value = _fake_entity_entry("alexa_media")
        async_get.return_value = registry

        conflict = _notify_media_player_conflict(
            hass,
            notify_targets=["notify.alexa_media_echo_salon"],
            media_player_targets=["media_player.echo_salon"],
        )

    assert conflict is True


def test_notify_media_player_conflict_false_for_different_devices():
    hass = MagicMock()
    with patch("custom_components.programme_tnt_fr.config_flow.er.async_get") as async_get:
        registry = MagicMock()
        registry.async_get.return_value = _fake_entity_entry("alexa_media")
        async_get.return_value = registry

        conflict = _notify_media_player_conflict(
            hass,
            notify_targets=["notify.alexa_media_echo_chambre"],
            media_player_targets=["media_player.echo_salon"],
        )

    assert conflict is False


def test_notify_media_player_conflict_false_for_non_alexa_media_player():
    hass = MagicMock()
    with patch("custom_components.programme_tnt_fr.config_flow.er.async_get") as async_get:
        registry = MagicMock()
        registry.async_get.return_value = _fake_entity_entry("cast")
        async_get.return_value = registry

        conflict = _notify_media_player_conflict(
            hass,
            notify_targets=["notify.mobile_app_iphone_fred"],
            media_player_targets=["media_player.tv_salon"],
        )

    assert conflict is False


def test_notify_media_player_conflict_false_when_either_list_empty():
    hass = MagicMock()
    assert _notify_media_player_conflict(hass, [], ["media_player.echo_salon"]) is False
    assert _notify_media_player_conflict(hass, ["notify.alexa_media_echo_salon"], []) is False
