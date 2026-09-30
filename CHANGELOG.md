# Changelog

Historique des versions de l'integration Programme TNT FR. Reconstitue a partir du
manifest.json et de l'historique Git ; le detail complet reste dans l'historique des
commits.

## 3.0.0 - 2026-09-29
Version majeure de communication avec TMDB (breaking change).

- Delai progressif (backoff exponentiel) sur les echecs de recherche d'affiche TMDB :
  apres un echec, le prochain essai pour ce titre est reporte (5 min, 10, 20 min...),
  jusqu'a un plafond de 240 minutes, au lieu de retenter a chaque cycle de
  rafraichissement. Evite une charge de fond permanente sur l'API TMDB, notamment
  avec la cle TMDB partagee.
- README : recommande fortement l'usage d'une cle TMDB personnelle pour eviter le
  rate limit de la cle partagee.

## 2.5.14 - 2026-09-29
- Corrige les collisions de titres homonymes dans le cache TMDB : le cache est desormais
  indexe par (titre, categorie) plutot que par titre seul.

## 2.5.13 - 2026-09-28
- Corrige le decalage de version de la carte Lovelace (CARD_VERSION resynchronise
  avec le manifest).

## 2.5.11 - 2.5.12 - 2026-09-28
- Purge le cache TMDB des titres qui ne sont plus presents dans le flux XMLTV, et
  couverture de tests ajoutee pour cette purge.
- Evite un faux rapprochement TMDB vers un film pour les programmes de type societe /
  debat.

## 2.5.1 - 2.5.10 - 2026-09-20 / 2026-09-21
Serie rapide de correctifs mineurs et de resynchronisations de version entre le
manifest et la carte Lovelace (aucune release ne comporte de description detaillee
individuelle dans l'historique Git).

## 2.5.0 - 2026-09-20
- Ajoute la prise en charge des chaines belges (rangee A a suivre).

## Versions anterieures a 2.5.0
Non detaillees ici ; se referer a l'historique Git du depot.
