"""Unit tests for the pure logic helpers in coordinator.py.

These tests only exercise static methods with no I/O, no Home Assistant
runtime, and no coordinator instance - title normalization and
category/title matching, which is exactly the logic that has caused real
regressions in the past (French spelled-out numbers vs digits in v2.1.17,
"Meteo" vs "Miss Meteo" false-positive matches fixed in v2.1.15).
"""
from custom_components.programme_tnt_fr.coordinator import ProgrammeTntFrCoordinator


def test_normalize_title_strips_accents_and_lowercases():
    assert ProgrammeTntFrCoordinator._normalize_title("Ete") == "ete"
    assert ProgrammeTntFrCoordinator._normalize_title("Symphonie pour un massacre") == (
        "symphonie pour un massacre"
    )


def test_normalize_title_converts_french_spelled_out_numbers():
    assert ProgrammeTntFrCoordinator._normalize_title("Les douze coups de midi") == (
        "les 12 coups de midi"
    )
    assert ProgrammeTntFrCoordinator._normalize_title("Dix-sept ans") == "17 ans"


def test_normalize_title_empty_and_none():
    assert ProgrammeTntFrCoordinator._normalize_title("") == ""
    assert ProgrammeTntFrCoordinator._normalize_title(None) == ""


def test_titles_match_prefix_handles_episode_suffix():
    query = ProgrammeTntFrCoordinator._normalize_title("Koh-Lanta - S29E01")
    candidate = ProgrammeTntFrCoordinator._normalize_title("Koh-Lanta")
    assert ProgrammeTntFrCoordinator._titles_match(query, candidate) is True


def test_titles_match_rejects_loose_fulltext_match():
    query = ProgrammeTntFrCoordinator._normalize_title("Meteo")
    candidate = ProgrammeTntFrCoordinator._normalize_title("Miss Meteo")
    assert ProgrammeTntFrCoordinator._titles_match(query, candidate) is False


def test_titles_match_french_number_words_vs_digits():
    query = ProgrammeTntFrCoordinator._normalize_title("Les douze coups de midi")
    candidate = ProgrammeTntFrCoordinator._normalize_title("Les 12 coups de midi")
    assert ProgrammeTntFrCoordinator._titles_match(query, candidate) is True


def test_is_movie_category_true_cases():
    assert ProgrammeTntFrCoordinator._is_movie_category("Film") is True
    assert ProgrammeTntFrCoordinator._is_movie_category("long metrage") is True
    assert ProgrammeTntFrCoordinator._is_movie_category("Cinema francais") is True


def test_is_movie_category_false_cases():
    assert ProgrammeTntFrCoordinator._is_movie_category(None) is False
    assert ProgrammeTntFrCoordinator._is_movie_category("") is False
    assert ProgrammeTntFrCoordinator._is_movie_category("Action") is False
    assert ProgrammeTntFrCoordinator._is_movie_category("Serie") is False
