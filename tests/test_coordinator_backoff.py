"""Tests for the TMDB lookup retry backoff added in v3.0.0
(_resolve_tmdb_posters / _tmdb_failure_counts / _tmdb_retry_after in
coordinator.py): delay progression, the 240-minute cap, and that a
title still inside its backoff window is skipped by the next refresh
cycle instead of being retried every 5 minutes regardless.

No pytest-homeassistant-custom-component fixtures are set up in this
repo (see conftest.py and .github/workflows/tests.yml, which only
installs plain homeassistant + pytest), so these tests use plain
asyncio.run() (no @pytest.mark.asyncio) and build the coordinator via
__new__ (same pattern as test_coordinator.py's _coordinator_with),
bypassing __init__ since it needs a live Home Assistant instance just
to open an aiohttp session these tests never use.
"""
import asyncio
from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock

from homeassistant.util import dt as dt_util

from custom_components.programme_tnt_fr.coordinator import (
    Programme,
    ProgrammeTntFrCoordinator,
)

def run(coro):
    return asyncio.run(coro)

def _coordinator():
    coordinator = ProgrammeTntFrCoordinator.__new__(ProgrammeTntFrCoordinator)
    coordinator._tmdb_poster_cache = {}
    coordinator._tmdb_pending_titles = set()
    coordinator._tmdb_failure_counts = {}
    coordinator._tmdb_retry_after = {}
    coordinator._tmdb_auth_warned = False
    coordinator._tmdb_own_key_recommended = True
    coordinator._tmdb_api_key = "test-key"
    return coordinator

def _programme(start, stop, title):
    return Programme(
        start=start,
        stop=stop,
        title=title,
        subtitle=None,
        desc=None,
        category=None,
        icon=None,
        rating=None,
        date=None,
    )

def test_backoff_delay_doubles_on_each_consecutive_failure():
    coordinator = _coordinator()
    coordinator._lookup_tmdb_poster = AsyncMock(side_effect=Exception("boom"))
    key = ("Titre en echec", None)

    run(coordinator._resolve_tmdb_posters({key: None}))
    assert coordinator._tmdb_failure_counts[key] == 1
    delay = coordinator._tmdb_retry_after[key] - dt_util.now()
    assert timedelta(minutes=4) < delay <= timedelta(minutes=5)

    run(coordinator._resolve_tmdb_posters({key: None}))
    assert coordinator._tmdb_failure_counts[key] == 2
    delay = coordinator._tmdb_retry_after[key] - dt_util.now()
    assert timedelta(minutes=9) < delay <= timedelta(minutes=10)

    run(coordinator._resolve_tmdb_posters({key: None}))
    assert coordinator._tmdb_failure_counts[key] == 3
    delay = coordinator._tmdb_retry_after[key] - dt_util.now()
    assert timedelta(minutes=19) < delay <= timedelta(minutes=20)

def test_backoff_caps_at_240_minutes_after_enough_failures():
    coordinator = _coordinator()
    coordinator._lookup_tmdb_poster = AsyncMock(side_effect=Exception("boom"))
    key = ("Titre toujours en echec", None)

    for _ in range(8):
        run(coordinator._resolve_tmdb_posters({key: None}))

    assert coordinator._tmdb_failure_counts[key] == 8
    delay = coordinator._tmdb_retry_after[key] - dt_util.now()
    assert timedelta(minutes=239) < delay <= timedelta(minutes=240)

def test_backoff_resets_on_success_after_previous_failures():
    coordinator = _coordinator()
    coordinator._lookup_tmdb_poster = AsyncMock(side_effect=Exception("boom"))
    key = ("Titre qui finit par reussir", None)

    run(coordinator._resolve_tmdb_posters({key: None}))
    assert coordinator._tmdb_failure_counts[key] == 1

    coordinator._lookup_tmdb_poster = AsyncMock(return_value=None)
    run(coordinator._resolve_tmdb_posters({key: None}))

    assert key not in coordinator._tmdb_failure_counts
    assert key not in coordinator._tmdb_retry_after
    assert coordinator._tmdb_poster_cache[key] is None

def test_async_update_data_skips_title_still_within_backoff_window():
    now = dt_util.now()
    coordinator = _coordinator()
    coordinator._channels = ["TF1.fr"]
    coordinator._last_fetch = now
    coordinator._programmes_by_channel = {
        "TF1.fr": [
            _programme(
                now - timedelta(minutes=30), now + timedelta(minutes=30), "En echec"
            )
        ]
    }
    coordinator._channels_meta = {}
    coordinator._tmdb_failure_counts = {("En echec", None): 3}
    coordinator._tmdb_retry_after = {("En echec", None): now + timedelta(minutes=15)}

    hass = MagicMock()
    hass.async_create_task = MagicMock()
    coordinator.hass = hass

    run(coordinator._async_update_data())

    hass.async_create_task.assert_not_called()

def test_async_update_data_retries_title_once_backoff_window_elapsed():
    now = dt_util.now()
    coordinator = _coordinator()
    coordinator._channels = ["TF1.fr"]
    coordinator._last_fetch = now
    coordinator._programmes_by_channel = {
        "TF1.fr": [
            _programme(
                now - timedelta(minutes=30),
                now + timedelta(minutes=30),
                "Pret a reessayer",
            )
        ]
    }
    coordinator._channels_meta = {}
    coordinator._tmdb_failure_counts = {("Pret a reessayer", None): 3}
    coordinator._tmdb_retry_after = {
        ("Pret a reessayer", None): now - timedelta(minutes=1)
    }

    hass = MagicMock()
    hass.async_create_task = MagicMock()
    coordinator.hass = hass

    run(coordinator._async_update_data())

    hass.async_create_task.assert_called_once()
