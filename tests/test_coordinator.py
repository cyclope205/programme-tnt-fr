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
    # "Les" est egalement retire (article de tete), voir
    # test_normalize_title_strips_leading_article_* : "12 coups de midi" est
    # le resultat attendu, pas "les 12 coups de midi".
    assert ProgrammeTntFrCoordinator._normalize_title("Les douze coups de midi") == (
        "12 coups de midi"
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


def test_clean_search_query_strips_episode_subtitle_and_season():
    cleaned, year = ProgrammeTntFrCoordinator._clean_search_query(
        "Candice Renoir (Faute avouee a demi-pardonnee) S5 (1/10)"
    )
    assert cleaned == "Candice Renoir"
    assert year is None


def test_clean_search_query_extracts_reboot_year_marker():
    cleaned, year = ProgrammeTntFrCoordinator._clean_search_query(
        "Magnum *2018 (La passagere) S5 (1/20)"
    )
    assert cleaned == "Magnum"
    assert year == "2018"


def test_clean_search_query_strips_season_suffix_without_parens():
    cleaned, year = ProgrammeTntFrCoordinator._clean_search_query(
        "In Flight S1 (1/6)"
    )
    assert cleaned == "In Flight"
    assert year is None


def test_clean_search_query_preserves_colon_in_real_title():
    cleaned, year = ProgrammeTntFrCoordinator._clean_search_query(
        "Toronto : Section criminelle (La vraie Eve) S1 (3/10)"
    )
    assert cleaned == "Toronto : Section criminelle"
    assert year is None


def test_clean_search_query_leaves_clean_titles_unchanged():
    # Titres de films (sans metadonnees d'episode) : aucun effet de bord.
    cleaned, year = ProgrammeTntFrCoordinator._clean_search_query("Kon-Tiki")
    assert cleaned == "Kon-Tiki"
    assert year is None


def test_clean_search_query_empty_and_none():
    assert ProgrammeTntFrCoordinator._clean_search_query("") == ("", None)
    assert ProgrammeTntFrCoordinator._clean_search_query(None) == ("", None)


def test_normalize_title_unifies_punctuation_separators():
    # Meme documentaire, ponctuation differente entre XMLTV et TMDB.
    xmltv = ProgrammeTntFrCoordinator._normalize_title(
        "Giscard et l'Europe, chronique d'un reve inacheve"
    )
    tmdb = ProgrammeTntFrCoordinator._normalize_title(
        "Giscard et l'Europe : chronique d'un reve inacheve"
    )
    assert xmltv == tmdb


def test_normalize_title_unifies_dash_and_colon():
    xmltv = ProgrammeTntFrCoordinator._normalize_title(
        "Irish Celtic : le chemin des legendes"
    )
    tmdb = ProgrammeTntFrCoordinator._normalize_title(
        "Irish Celtic - Le Chemin des Legendes"
    )
    assert xmltv == tmdb


def test_normalize_title_unifies_periods():
    # XMLTV "Dr Pimple Popper" vs TMDB "Dr. Pimple Popper" - verifie sur
    # une recherche TMDB reelle (meme fiche, poster reel).
    xmltv = ProgrammeTntFrCoordinator._normalize_title("Dr Pimple Popper")
    tmdb = ProgrammeTntFrCoordinator._normalize_title("Dr. Pimple Popper")
    assert xmltv == tmdb


def test_normalize_title_unifies_periods_in_initialism():
    # XMLTV "R.I.S. Police scientifique" vs TMDB "R.I.S, police scientifique"
    # - meme serie, ponctuation differente autour de l'initialisme.
    xmltv = ProgrammeTntFrCoordinator._normalize_title(
        "R.I.S. Police scientifique"
    )
    tmdb = ProgrammeTntFrCoordinator._normalize_title(
        "R.I.S, police scientifique"
    )
    assert xmltv == tmdb


def test_normalize_title_collapses_whitespace_after_punctuation_strip():
    assert ProgrammeTntFrCoordinator._normalize_title("A : B, C - D") == "a b c d"


def test_normalize_title_strips_leading_article_le():
    assert ProgrammeTntFrCoordinator._normalize_title("Le Meilleur Patissier") == (
        "meilleur patissier"
    )
    assert ProgrammeTntFrCoordinator._normalize_title("Meilleur Patissier") == (
        "meilleur patissier"
    )


def test_normalize_title_strips_leading_article_la_les_l():
    assert ProgrammeTntFrCoordinator._normalize_title("La Voix") == "voix"
    assert ProgrammeTntFrCoordinator._normalize_title("Les Experts") == "experts"
    assert ProgrammeTntFrCoordinator._normalize_title("L'amour est dans le pre") == (
        "amour est dans le pre"
    )


def test_normalize_title_leading_article_matches_across_sources():
    query = ProgrammeTntFrCoordinator._normalize_title("Grande Librairie")
    candidate = ProgrammeTntFrCoordinator._normalize_title("La Grande Librairie")
    assert query == candidate
    assert ProgrammeTntFrCoordinator._titles_match(query, candidate) is True


def test_normalize_title_does_not_strip_article_mid_title():
    # "le"/"la"/"les" ailleurs qu'en tete ne doivent pas etre touches.
    assert ProgrammeTntFrCoordinator._normalize_title(
        "L'amour est dans le pre"
    ) == "amour est dans le pre"


def test_normalize_title_strips_leading_english_article():
    # XMLTV "Big Bang Theory" vs TMDB "The Big Bang Theory" - verifie sur
    # une recherche TMDB reelle (meme fiche, poster reel).
    xmltv = ProgrammeTntFrCoordinator._normalize_title("Big Bang Theory")
    tmdb = ProgrammeTntFrCoordinator._normalize_title("The Big Bang Theory")
    assert xmltv == tmdb


def test_normalize_title_strips_tmdb_live_prefix():
    # TMDB: "C dans l'air" est catalogue "LIVE: C dans l'air", sans
    # equivalent dans le flux XMLTV.
    query = ProgrammeTntFrCoordinator._normalize_title("C dans l'air")
    candidate = ProgrammeTntFrCoordinator._normalize_title("LIVE: C dans l'air")
    assert query == candidate
    assert ProgrammeTntFrCoordinator._titles_match(query, candidate) is True


def test_normalize_title_does_not_strip_live_without_colon():
    # Un titre qui commence reellement par "Live" (sans le marqueur TMDB
    # precis "LIVE:") ne doit pas etre touche.
    assert ProgrammeTntFrCoordinator._normalize_title("Live Aid") == "live aid"


def test_clean_search_query_strips_n_degree_episode_marker():
    cleaned, year = ProgrammeTntFrCoordinator._clean_search_query(
        "Lucas l'araignee (Derriere la porte) S1 (n°72)"
    )
    assert cleaned == "Lucas l'araignee"
    assert year is None


def test_clean_search_query_strips_dash_season_episode_code():
    cleaned, year = ProgrammeTntFrCoordinator._clean_search_query(
        "Zig & Sharko - S04E61"
    )
    assert cleaned == "Zig & Sharko"
    assert year is None
    cleaned2, _ = ProgrammeTntFrCoordinator._clean_search_query("Mr Bean - S04E14")
    assert cleaned2 == "Mr Bean"


def test_clean_search_query_dash_episode_code_does_not_affect_clean_titles():
    # Un titre avec un tiret qui ne ressemble pas a un code SxxEyy doit
    # rester intact.
    assert ProgrammeTntFrCoordinator._clean_search_query("Spider-Man") == (
        "Spider-Man", None
    )


def test_clean_search_query_strips_spelled_out_saison_suffix():
    cleaned, year = ProgrammeTntFrCoordinator._clean_search_query(
        "Planete chefs - Saison 1"
    )
    assert cleaned == "Planete chefs"
    assert year is None


def test_clean_search_query_strips_bare_trailing_season():
    cleaned, year = ProgrammeTntFrCoordinator._clean_search_query("90' Enquetes S17")
    assert cleaned == "90' Enquetes"
    assert year is None
    cleaned2, _ = ProgrammeTntFrCoordinator._clean_search_query("Reporters S1")
    assert cleaned2 == "Reporters"
    cleaned3, _ = ProgrammeTntFrCoordinator._clean_search_query("Appels d'urgence S22")
    assert cleaned3 == "Appels d'urgence"


def test_clean_search_query_bare_season_is_last_resort_only():
    # Les motifs plus specifiques (parentheses, tiret+code) doivent gagner
    # sur le repli generique "S<n>" en fin de titre.
    cleaned, _ = ProgrammeTntFrCoordinator._clean_search_query(
        "Candice Renoir (Pas de fumee sans feu) S4 (8/10)"
    )
    assert cleaned == "Candice Renoir"
    cleaned2, _ = ProgrammeTntFrCoordinator._clean_search_query("Zig & Sharko - S04E61")
    assert cleaned2 == "Zig & Sharko"


def test_clean_search_query_strips_cumulative_episode_numbering():
    cleaned, year = ProgrammeTntFrCoordinator._clean_search_query(
        "Amour, gloire et beaute (9709) (n°9709)"
    )
    assert cleaned == "Amour, gloire et beaute"
    assert year is None


def test_truncate_at_first_separator_strips_descriptive_tagline():
    assert ProgrammeTntFrCoordinator._truncate_at_first_separator(
        "Nomade des mers, les escales de l'innovation"
    ) == "Nomade des mers"


def test_truncate_at_first_separator_protects_short_titles():
    # "Amour" seul avant la virgule : pas assez specifique, on ne tronque
    # pas (la virgule fait partie du vrai titre "Amour, gloire et beaute").
    assert ProgrammeTntFrCoordinator._truncate_at_first_separator(
        "Amour, gloire et beaute"
    ) is None


def test_truncate_at_first_separator_no_separator_returns_none():
    assert ProgrammeTntFrCoordinator._truncate_at_first_separator("Kon-Tiki") is None


def test_clean_search_query_strips_version_qualifier():
    # "Le bateau (version realisateur)" a une vraie fiche TMDB sous "Le
    # Bateau" ; le qualificatif de version n'existe pas cote TMDB.
    cleaned, year = ProgrammeTntFrCoordinator._clean_search_query(
        "Le bateau (version r\u00e9alisateur)"
    )
    assert cleaned == "Le bateau"
    assert year is None


def test_clean_search_query_strips_directors_cut_qualifier():
    cleaned, year = ProgrammeTntFrCoordinator._clean_search_query(
        "Rencontres du troisi\u00e8me type (Director's Cut)"
    )
    assert cleaned == "Rencontres du troisi\u00e8me type"
    assert year is None
