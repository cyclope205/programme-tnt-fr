"""Unit tests for the pure logic helpers in coordinator.py.

These tests only exercise static methods with no I/O, no Home Assistant
runtime, and no coordinator instance - title normalization and
category/title matching, which is exactly the logic that has caused real
regressions in the past (French spelled-out numbers vs digits in v2.1.17,
"Meteo" vs "Miss Meteo" false-positive matches fixed in v2.1.15).
"""
from datetime import datetime, timedelta, timezone

from custom_components.programme_tnt_fr.coordinator import (
    Programme,
    ProgrammeTntFrCoordinator,
    TmdbMatch,
)


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



def test_normalize_title_unifies_ampersand_and_et_xmltv_side():
    # XMLTV "Superman et Lo\u00efs" vs TMDB "Superman & Lo\u00efs" -
    # verifie sur une vraie fiche TMDB.
    xmltv = ProgrammeTntFrCoordinator._normalize_title("Superman et Lo\u00efs")
    tmdb = ProgrammeTntFrCoordinator._normalize_title("Superman & Lo\u00efs")
    assert xmltv == tmdb


def test_normalize_title_unifies_ampersand_and_et_tmdb_side():
    # Cas inverse : XMLTV utilise "&", TMDB "et" (ex: "Tom & Jerry et le
    # haricot geant" vs "Tom et Jerry et le haricot geant").
    xmltv = ProgrammeTntFrCoordinator._normalize_title(
        "Tom & Jerry et le haricot g\u00e9ant"
    )
    tmdb = ProgrammeTntFrCoordinator._normalize_title(
        "Tom et Jerry et le haricot g\u00e9ant"
    )
    assert xmltv == tmdb


def test_normalize_title_unifies_slash_separator():
    # XMLTV "Superman / Batman : Apocalypse" vs TMDB
    # "Superman/Batman: Apocalypse" - verifie sur une vraie fiche TMDB.
    xmltv = ProgrammeTntFrCoordinator._normalize_title(
        "Superman / Batman : Apocalypse"
    )
    tmdb = ProgrammeTntFrCoordinator._normalize_title("Superman/Batman: Apocalypse")
    assert xmltv == tmdb



def test_clean_search_query_strips_descriptive_subtitle_before_number_marker():
    # "Cuisines des terroirs (La Mac\u00e9doine du Nord) (n\u00b0311)" a
    # une vraie fiche TMDB sous "Cuisines des terroirs" ; sans marqueur de
    # saison entre les deux parentheses, aucun tier existant ne
    # s'appliquait avant ce correctif.
    cleaned, year = ProgrammeTntFrCoordinator._clean_search_query(
        "Cuisines des terroirs (La Mac\u00e9doine du Nord) (n\u00b0311)"
    )
    assert cleaned == "Cuisines des terroirs"
    assert year is None


def test_clean_search_query_strips_subtitle_marker_does_not_break_cumulative():
    # Le nouveau tier chevauche _CUMULATIVE_EPISODE_RE (sous-titre
    # purement numerique) sans le remplacer : ce dernier est tente en
    # premier, donc le resultat reste identique.
    cleaned, year = ProgrammeTntFrCoordinator._clean_search_query(
        "Amour, gloire et beaut\u00e9 (9709) (n\u00b09709)"
    )
    assert cleaned == "Amour, gloire et beaut\u00e9"
    assert year is None



def test_normalize_title_unifies_curly_and_straight_apostrophe():
    # XMLTV "Le combat d'Alice" (apostrophe droite) vs TMDB
    # "Le combat d’Alice" (apostrophe courbe typographique) - verifie
    # sur une vraie fiche TMDB.
    xmltv = ProgrammeTntFrCoordinator._normalize_title("Le combat d'Alice")
    tmdb = ProgrammeTntFrCoordinator._normalize_title("Le combat d’Alice")
    assert xmltv == tmdb



def test_build_tmdb_match_extracts_rating_and_votes():
    result = {
        "id": 123456,
        "poster_path": "/abc.jpg",
        "vote_average": 8.234,
        "vote_count": 15432,
    }
    match = ProgrammeTntFrCoordinator._build_tmdb_match(result, "movie")
    assert match == TmdbMatch(
        poster="/abc.jpg",
        tmdb_id=123456,
        media_type="movie",
        rating=8.234,
        votes=15432,
    )


def test_build_tmdb_match_defaults_missing_rating_and_votes_to_zero():
    # Certaines fiches TMDB (notamment les tres recentes) n'ont pas encore
    # de note ni de votes : doit degrader proprement vers 0, pas planter ni
    # renvoyer None (l'automatisation HA doit pouvoir comparer sans erreur).
    result = {"id": 42, "poster_path": "/xyz.jpg"}
    match = ProgrammeTntFrCoordinator._build_tmdb_match(result, "tv")
    assert match == TmdbMatch(
        poster="/xyz.jpg", tmdb_id=42, media_type="tv", rating=0, votes=0
    )


def test_build_tmdb_match_preserves_media_type():
    result = {"id": 1, "poster_path": "/a.jpg"}
    assert ProgrammeTntFrCoordinator._build_tmdb_match(result, "movie").media_type == "movie"
    assert ProgrammeTntFrCoordinator._build_tmdb_match(result, "tv").media_type == "tv"


# ---------------------------------------------------------------------------
# _parse_xmltv: XMLTV feed parsing (static method, no I/O - the network
# fetch and the executor-thread dispatch around it live in
# _fetch_and_parse and are not covered here).
# ---------------------------------------------------------------------------

_XML_VALID_PROGRAMME = """<?xml version="1.0" encoding="UTF-8"?>
<tv>
  <channel id="TF1.fr">
    <display-name>TF1</display-name>
    <icon src="https://example.com/tf1.png"/>
  </channel>
  <programme start="20260821200000 +0200" stop="20260821220000 +0200" channel="TF1.fr">
    <title>Journal de 20h</title>
    <sub-title>Edition speciale</sub-title>
    <desc>Le journal du soir.</desc>
    <category>Information</category>
    <icon src="https://example.com/journal.png"/>
    <rating>
      <value>10</value>
    </rating>
  </programme>
</tv>
"""


def test_parse_xmltv_parses_channel_and_full_programme():
    channels_meta, programmes = ProgrammeTntFrCoordinator._parse_xmltv(
        _XML_VALID_PROGRAMME, {"TF1.fr"}
    )
    assert channels_meta["TF1.fr"]["name"] == "TF1"
    assert channels_meta["TF1.fr"]["icon"] == "https://example.com/tf1.png"
    assert list(programmes.keys()) == ["TF1.fr"]
    prog = programmes["TF1.fr"][0]
    assert prog.title == "Journal de 20h"
    assert prog.subtitle == "Edition speciale"
    assert prog.desc == "Le journal du soir."
    assert prog.category == "Information"
    assert prog.icon == "https://example.com/journal.png"
    assert prog.rating == "10"
    assert (prog.start.hour, prog.start.minute) == (20, 0)
    assert (prog.stop.hour, prog.stop.minute) == (22, 0)


_XML_UNWANTED_CHANNEL = """<?xml version="1.0" encoding="UTF-8"?>
<tv>
  <channel id="TF1.fr"><display-name>TF1</display-name></channel>
  <programme start="20260821200000 +0200" stop="20260821220000 +0200" channel="TF1.fr">
    <title>Journal de 20h</title>
  </programme>
</tv>
"""


def test_parse_xmltv_skips_programme_for_channel_not_in_wanted():
    channels_meta, programmes = ProgrammeTntFrCoordinator._parse_xmltv(
        _XML_UNWANTED_CHANNEL, {"France2.fr"}
    )
    assert programmes == {}
    # Channel metadata is collected for every <channel> element regardless
    # of `wanted` - only <programme> entries are filtered by it.
    assert "TF1.fr" in channels_meta


_XML_MISSING_OR_INVALID_TIMES = """<?xml version="1.0" encoding="UTF-8"?>
<tv>
  <channel id="TF1.fr"><display-name>TF1</display-name></channel>
  <programme stop="20260821220000 +0200" channel="TF1.fr">
    <title>Sans heure de debut</title>
  </programme>
  <programme start="20260821220000 +0200" channel="TF1.fr">
    <title>Sans heure de fin</title>
  </programme>
  <programme start="not-a-date" stop="20260821220000 +0200" channel="TF1.fr">
    <title>Date invalide</title>
  </programme>
</tv>
"""


def test_parse_xmltv_skips_programmes_with_missing_or_invalid_start_stop():
    _, programmes = ProgrammeTntFrCoordinator._parse_xmltv(
        _XML_MISSING_OR_INVALID_TIMES, {"TF1.fr"}
    )
    assert programmes.get("TF1.fr", []) == []


_XML_MINIMAL_PROGRAMME = """<?xml version="1.0" encoding="UTF-8"?>
<tv>
  <channel id="TF1.fr"><display-name>TF1</display-name></channel>
  <programme start="20260821200000 +0200" stop="20260821203000 +0200" channel="TF1.fr">
  </programme>
</tv>
"""


def test_parse_xmltv_missing_optional_fields_default_gracefully():
    _, programmes = ProgrammeTntFrCoordinator._parse_xmltv(
        _XML_MINIMAL_PROGRAMME, {"TF1.fr"}
    )
    prog = programmes["TF1.fr"][0]
    assert prog.title == ""
    assert prog.subtitle is None
    assert prog.desc is None
    assert prog.category is None
    assert prog.icon is None
    assert prog.rating is None


_XML_CHANNEL_WITHOUT_ID = """<?xml version="1.0" encoding="UTF-8"?>
<tv>
  <channel><display-name>Chaine fantome</display-name></channel>
  <channel id="TF1.fr"><display-name>TF1</display-name></channel>
</tv>
"""


def test_parse_xmltv_skips_channel_element_without_id():
    channels_meta, _ = ProgrammeTntFrCoordinator._parse_xmltv(
        _XML_CHANNEL_WITHOUT_ID, {"TF1.fr"}
    )
    assert list(channels_meta.keys()) == ["TF1.fr"]


_XML_CHANNEL_WITHOUT_NAME = """<?xml version="1.0" encoding="UTF-8"?>
<tv>
  <channel id="M6.fr"></channel>
</tv>
"""


def test_parse_xmltv_channel_meta_defaults_name_to_id_and_icon_to_none():
    channels_meta, _ = ProgrammeTntFrCoordinator._parse_xmltv(
        _XML_CHANNEL_WITHOUT_NAME, {"M6.fr"}
    )
    assert channels_meta["M6.fr"] == {"name": "M6.fr", "icon": None}


_XML_UNSORTED_PROGRAMMES = """<?xml version="1.0" encoding="UTF-8"?>
<tv>
  <channel id="TF1.fr"><display-name>TF1</display-name></channel>
  <programme start="20260821220000 +0200" stop="20260821223000 +0200" channel="TF1.fr">
    <title>Second</title>
  </programme>
  <programme start="20260821200000 +0200" stop="20260821220000 +0200" channel="TF1.fr">
    <title>Premier</title>
  </programme>
</tv>
"""


def test_parse_xmltv_sorts_programmes_by_start_time():
    # Le flux XMLTV reel ne garantit pas l'ordre chronologique par chaine -
    # _pick_slots s'appuie sur ce tri pour ses boucles "premier programme
    # qui demarre apres X".
    _, programmes = ProgrammeTntFrCoordinator._parse_xmltv(
        _XML_UNSORTED_PROGRAMMES, {"TF1.fr"}
    )
    titles = [p.title for p in programmes["TF1.fr"]]
    assert titles == ["Premier", "Second"]


_XML_MULTI_CHANNEL = """<?xml version="1.0" encoding="UTF-8"?>
<tv>
  <channel id="TF1.fr"><display-name>TF1</display-name></channel>
  <channel id="M6.fr"><display-name>M6</display-name></channel>
  <programme start="20260821200000 +0200" stop="20260821210000 +0200" channel="TF1.fr">
    <title>TF1 20h</title>
  </programme>
  <programme start="20260821200000 +0200" stop="20260821210000 +0200" channel="M6.fr">
    <title>M6 20h</title>
  </programme>
  <programme start="20260821200000 +0200" stop="20260821210000 +0200" channel="UnknownChannel.fr">
    <title>Inconnu</title>
  </programme>
</tv>
"""


def test_parse_xmltv_filters_to_wanted_channels_only():
    _, programmes = ProgrammeTntFrCoordinator._parse_xmltv(
        _XML_MULTI_CHANNEL, {"TF1.fr", "M6.fr"}
    )
    assert set(programmes.keys()) == {"TF1.fr", "M6.fr"}


# ---------------------------------------------------------------------------
# _pick_slots: current / prime_time / second_part selection.
#
# Built via __new__ instead of the real constructor, since __init__ needs
# a live Home Assistant instance (async_get_clientsession(hass)) just to
# open an aiohttp session it never uses here - _pick_slots only ever
# reads self._programmes_by_channel.
# ---------------------------------------------------------------------------

_TZ = timezone(timedelta(hours=2))


def _dt(day, hour, minute):
    """Tz-aware datetime on August <day>, 2026, fixed +02:00 offset.

    Matches the "+0200" offset used by the real XMLTV feed, but any
    consistent offset works here since _pick_slots only ever compares
    datetimes that already share the same tzinfo.
    """
    return datetime(2026, 8, day, hour, minute, tzinfo=_TZ)


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
    )


def _coordinator_with(programmes, channel_id="TF1.fr"):
    coordinator = ProgrammeTntFrCoordinator.__new__(ProgrammeTntFrCoordinator)
    coordinator._programmes_by_channel = {channel_id: programmes}
    return coordinator


def test_pick_slots_current_is_programme_covering_now():
    progs = [
        _programme(_dt(10, 19, 0), _dt(10, 20, 0), "Avant"),
        _programme(_dt(10, 20, 0), _dt(10, 21, 0), "En cours"),
        _programme(_dt(10, 21, 0), _dt(10, 22, 0), "Apres"),
    ]
    coordinator = _coordinator_with(progs)
    current, _, _ = coordinator._pick_slots("TF1.fr", _dt(10, 20, 30))
    assert current.title == "En cours"


def test_pick_slots_current_none_when_now_falls_in_a_gap():
    # Coupure publicitaire / trou dans le flux entre deux programmes.
    progs = [
        _programme(_dt(10, 19, 0), _dt(10, 20, 0), "Avant"),
        _programme(_dt(10, 20, 5), _dt(10, 21, 0), "Apres coupure"),
    ]
    coordinator = _coordinator_with(progs)
    current, _, _ = coordinator._pick_slots("TF1.fr", _dt(10, 20, 2))
    assert current is None


def test_pick_slots_prime_time_is_programme_covering_threshold():
    progs = [
        _programme(_dt(10, 20, 0), _dt(10, 21, 15), "Avant-soiree"),
        _programme(_dt(10, 21, 15), _dt(10, 23, 0), "Prime"),
    ]
    coordinator = _coordinator_with(progs)
    _, prime_time, _ = coordinator._pick_slots("TF1.fr", _dt(10, 18, 0))
    assert prime_time.title == "Prime"


def test_pick_slots_prime_time_falls_back_to_next_programme_when_gap_at_threshold():
    # Aucun programme ne couvre exactement 21h15 (retard antenne) : on
    # prend le premier qui demarre juste apres, pas le precedent.
    progs = [
        _programme(_dt(10, 20, 0), _dt(10, 21, 10), "Avant"),
        _programme(_dt(10, 21, 30), _dt(10, 23, 0), "Retard antenne"),
    ]
    coordinator = _coordinator_with(progs)
    _, prime_time, _ = coordinator._pick_slots("TF1.fr", _dt(10, 18, 0))
    assert prime_time.title == "Retard antenne"


def test_pick_slots_second_part_corrects_when_same_programme_as_prime_time():
    # Un programme unique couvre a la fois 21h15 et 22h40 (long film) :
    # second_part doit alors sauter au programme SUIVANT, pas dupliquer
    # prime_time.
    progs = [
        _programme(_dt(10, 21, 15), _dt(10, 23, 30), "Long film"),
        _programme(_dt(10, 23, 30), _dt(10, 23, 59), "Late news"),
    ]
    coordinator = _coordinator_with(progs)
    _, prime_time, second_part = coordinator._pick_slots("TF1.fr", _dt(10, 20, 0))
    assert prime_time.title == "Long film"
    assert second_part.title == "Late news"


def test_pick_slots_second_part_none_when_nothing_follows_prime_time():
    progs = [
        _programme(_dt(10, 21, 15), _dt(10, 23, 59), "Seul programme de la soiree"),
    ]
    coordinator = _coordinator_with(progs)
    _, prime_time, second_part = coordinator._pick_slots("TF1.fr", _dt(10, 20, 0))
    assert prime_time.title == "Seul programme de la soiree"
    assert second_part is None


def test_pick_slots_uses_previous_broadcast_day_before_day_reset():
    # now = 10 aout 02h00, avant DAY_RESET (05h00) : rattache a la soiree
    # du 9 aout, pas a celle du 10 (qui n'a pas encore commence).
    progs = [
        _programme(_dt(9, 21, 15), _dt(9, 23, 0), "Prime de la veille"),
        _programme(_dt(10, 21, 15), _dt(10, 23, 0), "Prime du jour meme"),
    ]
    coordinator = _coordinator_with(progs)
    _, prime_time, _ = coordinator._pick_slots("TF1.fr", _dt(10, 2, 0))
    assert prime_time.title == "Prime de la veille"


def test_pick_slots_empty_programme_list_returns_all_none():
    coordinator = _coordinator_with([])
    current, prime_time, second_part = coordinator._pick_slots("TF1.fr", _dt(10, 20, 0))
    assert current is None
    assert prime_time is None
    assert second_part is None


def test_pick_slots_unknown_channel_returns_all_none():
    coordinator = _coordinator_with(
        [_programme(_dt(10, 21, 15), _dt(10, 22, 0), "X")]
    )
    current, prime_time, second_part = coordinator._pick_slots(
        "UnknownChannel.fr", _dt(10, 20, 0)
    )
    assert current is None
    assert prime_time is None
    assert second_part is None
