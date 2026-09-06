"""Unit tests for reminders.py.

No pytest-homeassistant-custom-component fixtures are set up in this repo
(see conftest.py - a bare sys.path shim - and .github/workflows/tests.yml,
which only installs plain `homeassistant` + `pytest`, no async plugin).
So these tests use plain asyncio.run() for coroutines (no
@pytest.mark.asyncio), lightweight MagicMock/fake stand-ins for
hass/config entries instead of a real HomeAssistant core instance, and
patch out async_track_point_in_time for the tests that reach the actual
timer-scheduling call - that HA helper needs a real event-loop-integrated
hass object it would not get from a bare MagicMock.
"""
import asyncio
from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.exceptions import ServiceValidationError
from homeassistant.util import dt as dt_util

from custom_components.programme_tnt_fr.reminders import (
    _UNSUB_KEY,
    _ReminderManager,
    _reminder_id,
)


class _FakeConfigEntry:
    def __init__(self, data=None, options=None):
        self.data = data or {}
        self.options = options or {}


class _FakeStore:
    def __init__(self, initial=None):
        self._data = initial

    async def async_load(self):
        return self._data

    async def async_save(self, data):
        self._data = data


class _FakeCall:
    def __init__(self, data):
        self.data = data


def _make_hass(entries=None):
    hass = MagicMock()
    hass.config_entries.async_entries.return_value = entries or []
    hass.data = {}
    hass.services.async_call = AsyncMock()
    hass.services.has_service = MagicMock(return_value=False)
    return hass


def run(coro):
    return asyncio.run(coro)


# --- _reminder_id ---------------------------------------------------------

def test_reminder_id_is_deterministic():
    a = _reminder_id("TF1", "JT", "2026-09-06T20:00:00+02:00", 10, "Fred")
    b = _reminder_id("TF1", "JT", "2026-09-06T20:00:00+02:00", 10, "Fred")
    assert a == b


def test_reminder_id_differs_per_profile():
    # Two profiles scheduling the same program/delay must not collide.
    fred = _reminder_id("TF1", "JT", "2026-09-06T20:00:00+02:00", 10, "Fred")
    ginie = _reminder_id("TF1", "JT", "2026-09-06T20:00:00+02:00", 10, "Ginie")
    assert fred != ginie


def test_reminder_id_differs_per_minutes_before():
    a = _reminder_id("TF1", "JT", "2026-09-06T20:00:00+02:00", 5, None)
    b = _reminder_id("TF1", "JT", "2026-09-06T20:00:00+02:00", 15, None)
    assert a != b


# --- target resolution ------------------------------------------------

def test_resolve_notify_targets_strips_notify_prefix():
    hass = _make_hass([_FakeConfigEntry(options={"notify_target": ["notify.mobile_app_iphone_fred"]})])
    manager = _ReminderManager(hass, _FakeStore())
    assert manager._resolve_notify_targets() == ["mobile_app_iphone_fred"]


def test_resolve_notify_targets_empty_when_none_configured():
    hass = _make_hass([_FakeConfigEntry()])
    manager = _ReminderManager(hass, _FakeStore())
    assert manager._resolve_notify_targets() == []


def test_find_profile_matches_by_name():
    hass = _make_hass([
        _FakeConfigEntry(options={"reminder_profiles": [{"name": "Fred"}, {"name": "Ginie"}]})
    ])
    manager = _ReminderManager(hass, _FakeStore())
    assert manager._find_profile("Ginie") == {"name": "Ginie"}
    assert manager._find_profile("Unknown") is None
    assert manager._find_profile(None) is None


def test_resolve_targets_uses_profile_when_found():
    hass = _make_hass([
        _FakeConfigEntry(options={
            "reminder_profiles": [{
                "name": "Fred",
                "notify_target": ["notify.mobile_app_iphone_fred"],
                "media_player_targets": ["media_player.echo_salon"],
                "tts_engine": "tts.piper",
            }]
        })
    ])
    manager = _ReminderManager(hass, _FakeStore())
    targets, media_targets, tts = manager._resolve_targets("Fred")
    assert targets == ["mobile_app_iphone_fred"]
    assert media_targets == ["media_player.echo_salon"]
    assert tts == "tts.piper"


def test_resolve_targets_falls_back_to_global_when_profile_not_found():
    hass = _make_hass([
        _FakeConfigEntry(options={"notify_target": ["notify.mobile_app_iphone_fred"]})
    ])
    manager = _ReminderManager(hass, _FakeStore())
    targets, media_targets, tts = manager._resolve_targets("Unknown")
    assert targets == ["mobile_app_iphone_fred"]
    assert media_targets == []
    assert tts is None


# --- _alexa_notify_slug -------------------------------------------------

def test_alexa_notify_slug_returns_slug_for_alexa_media_device():
    hass = _make_hass([])
    manager = _ReminderManager(hass, _FakeStore())
    with patch("custom_components.programme_tnt_fr.reminders.er.async_get") as async_get:
        registry = MagicMock()
        entry = MagicMock()
        entry.platform = "alexa_media"
        registry.async_get.return_value = entry
        async_get.return_value = registry

        slug = manager._alexa_notify_slug("media_player.echo_salon")

    assert slug == "alexa_media_echo_salon"


def test_alexa_notify_slug_none_for_non_alexa_device():
    hass = _make_hass([])
    manager = _ReminderManager(hass, _FakeStore())
    with patch("custom_components.programme_tnt_fr.reminders.er.async_get") as async_get:
        registry = MagicMock()
        entry = MagicMock()
        entry.platform = "cast"
        registry.async_get.return_value = entry
        async_get.return_value = registry

        slug = manager._alexa_notify_slug("media_player.tv_salon")

    assert slug is None


# --- async_handle_schedule validation ------------------------------------

def test_schedule_rejects_when_no_target_configured():
    hass = _make_hass([_FakeConfigEntry()])
    manager = _ReminderManager(hass, _FakeStore())
    call = _FakeCall({
        "channel_name": "TF1",
        "program_title": "JT",
        "start_time": (dt_util.now() + timedelta(hours=1)).isoformat(),
        "minutes_before": 10,
    })
    with pytest.raises(ServiceValidationError):
        run(manager.async_handle_schedule(call))


def test_schedule_rejects_invalid_start_time():
    hass = _make_hass([
        _FakeConfigEntry(options={"notify_target": ["notify.mobile_app_iphone_fred"]})
    ])
    manager = _ReminderManager(hass, _FakeStore())
    call = _FakeCall({
        "channel_name": "TF1",
        "program_title": "JT",
        "start_time": "not-a-date",
        "minutes_before": 10,
    })
    with pytest.raises(ServiceValidationError):
        run(manager.async_handle_schedule(call))


def test_schedule_rejects_when_too_late():
    hass = _make_hass([
        _FakeConfigEntry(options={"notify_target": ["notify.mobile_app_iphone_fred"]})
    ])
    manager = _ReminderManager(hass, _FakeStore())
    call = _FakeCall({
        "channel_name": "TF1",
        "program_title": "JT",
        # Starts in 5 minutes, but a 10-minute reminder would need to fire
        # 5 minutes in the past - must be rejected.
        "start_time": (dt_util.now() + timedelta(minutes=5)).isoformat(),
        "minutes_before": 10,
    })
    with pytest.raises(ServiceValidationError):
        run(manager.async_handle_schedule(call))


def test_schedule_success_saves_and_schedules_timer():
    hass = _make_hass([
        _FakeConfigEntry(options={"notify_target": ["notify.mobile_app_iphone_fred"]})
    ])
    store = _FakeStore()
    manager = _ReminderManager(hass, store)
    call = _FakeCall({
        "channel_name": "TF1",
        "program_title": "JT",
        "start_time": (dt_util.now() + timedelta(hours=1)).isoformat(),
        "minutes_before": 10,
    })

    with patch("custom_components.programme_tnt_fr.reminders.async_track_point_in_time") as track:
        track.return_value = MagicMock()
        run(manager.async_handle_schedule(call))

    assert track.called
    assert len(store._data["reminders"]) == 1
    saved = store._data["reminders"][0]
    assert saved["channel_name"] == "TF1"
    assert saved["targets"] == ["mobile_app_iphone_fred"]


# --- async_handle_cancel / async_handle_status ---------------------------

def test_cancel_removes_stored_reminder_and_unsub():
    hass = _make_hass([])
    reminder_id = _reminder_id("TF1", "JT", "2026-09-06T20:00:00", 10, None)
    unsub = MagicMock()
    hass.data[_UNSUB_KEY] = {reminder_id: unsub}
    store = _FakeStore({"reminders": [{"id": reminder_id, "channel_name": "TF1"}]})
    manager = _ReminderManager(hass, store)
    call = _FakeCall({
        "channel_name": "TF1",
        "program_title": "JT",
        "start_time": "2026-09-06T20:00:00",
        "minutes_before": 10,
    })

    run(manager.async_handle_cancel(call))

    unsub.assert_called_once()
    assert store._data["reminders"] == []


def test_status_reports_which_delays_are_scheduled():
    reminder_id_10 = _reminder_id("TF1", "JT", "2026-09-06T20:00:00", 10, None)
    hass = _make_hass([])
    store = _FakeStore({"reminders": [{"id": reminder_id_10}]})
    manager = _ReminderManager(hass, store)
    call = _FakeCall({
        "channel_name": "TF1",
        "program_title": "JT",
        "start_time": "2026-09-06T20:00:00",
    })

    result = run(manager.async_handle_status(call))

    assert result == {"scheduled_minutes": [10]}


# --- async_restore_pending -----------------------------------------------

def test_restore_pending_drops_expired_reminders():
    past = (dt_util.now() - timedelta(hours=1)).isoformat()
    future = (dt_util.now() + timedelta(hours=1)).isoformat()
    store = _FakeStore({
        "reminders": [
            {"id": "expired", "fire_time": past},
            {"id": "still_pending", "fire_time": future},
        ]
    })
    hass = _make_hass([])
    manager = _ReminderManager(hass, store)

    with patch("custom_components.programme_tnt_fr.reminders.async_track_point_in_time") as track:
        track.return_value = MagicMock()
        run(manager.async_restore_pending())

    assert track.call_count == 1  # only the still-pending one gets (re)scheduled
    assert [r["id"] for r in store._data["reminders"]] == ["still_pending"]
