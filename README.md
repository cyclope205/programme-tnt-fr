# Programme TNT FR

[![release](https://img.shields.io/github/v/release/cyclope205/programme-tnt-fr?label=release&color=blue)](https://github.com/cyclope205/programme-tnt-fr/releases)
[![build](https://github.com/cyclope205/programme-tnt-fr/actions/workflows/validate.yml/badge.svg)](https://github.com/cyclope205/programme-tnt-fr/actions/workflows/validate.yml)
[![license](https://img.shields.io/github/license/cyclope205/programme-tnt-fr)](LICENSE)
[![HACS: Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

<img src="https://raw.githubusercontent.com/cyclope205/programme-tnt-fr/main/custom_components/programme_tnt_fr/brand/logo.png" alt="Programme TNT FR" width="120">

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-cyclope205-ffdd00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/cyclope205)
[![PayPal](https://img.shields.io/badge/PayPal-Donate-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/cyclope205)

Integration Home Assistant qui recupere le programme TV des chaines francaises (TNT + une selection de chaines supplementaires) et l'affiche dans une carte Lovelace : carrousel "que regarder ce soir" et guide TV complet par chaine.

## Sommaire

- [Fonctionnalites](#fonctionnalites)
- [Captures d'ecran](#captures-decran)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation dans un tableau de bord](#utilisation-dans-un-tableau-de-bord)
- [Attributs disponibles](#attributs-disponibles)
- [A savoir](#a-savoir)

## Fonctionnalites

### Carrousel

Pour chaque chaine suivie, la carte affiche jusqu'a 3 programmes : celui en cours, la premiere partie de soiree et la deuxieme partie de soiree. Chaque vignette montre l'affiche du programme (recuperee sur TMDB quand une correspondance fiable est trouvee, sinon l'icone fournie par le flux TV), le titre, la categorie, la chaine et l'horaire. Un programme en cours de diffusion affiche un badge "Direct" et une barre de progression. Cliquer sur une vignette ouvre le detail du programme.

### Guide TV

Le bouton "Guide TV" dans l'entete de la carte bascule vers un guide complet, inspire de l'application Free : deux colonnes de chaines visibles a la fois, defilement horizontal pour changer de chaine (fleches sur ordinateur, glissement au doigt sur mobile/tablette) et defilement vertical pour parcourir la grille chronologique d'une chaine.

Le guide propose trois filtres, combinables :
- **Recherche** : un champ texte pour ne garder que les chaines dont le nom correspond.
- **Jour** : fleches precedent/suivant pour changer de journee de diffusion.
- **Horaire** : un menu pour n'afficher que les programmes d'une plage donnee (00h-06h, 06h-12h, 12h-16h, 16h-19h, 19h-21h, 21h-00h), pour retrouver rapidement un moment de la journee sans faire defiler toute la liste.

Un clic sur "Carrousel" dans l'entete revient a la vue de depart.

## Captures d'ecran

Ecran de configuration des chaines suivies :

![Ecran de configuration des chaines suivies](https://github.com/user-attachments/assets/179cca31-8e7c-466b-b5da-8c169168f9c2)

Vue "En ce moment" / "1ere partie de soiree" avec jaquettes TMDB :

![Rendu de la carte avec jaquettes TMDB](https://github.com/user-attachments/assets/ee3804a9-a729-4b10-820b-aa1d210eba1b)

Vue "2eme partie de soiree" :

![Vue 2eme partie de soiree](https://github.com/user-attachments/assets/39e629c2-02e7-43a5-bd89-fc73f2d7f03d)

Guide TV, avec le filtre horaire :

<!-- SCREENSHOT: Guide TV avec le filtre horaire (a remplacer ici) --><img width="462" height="792" alt="Capture d&#39;écran 2026-08-24 233655" src="https://github.com/user-attachments/assets/0e81bb5e-13af-473d-9f47-d30d67ddb0d9" />


## Installation

1. Ajouter ce depot a HACS comme depot personnalise :
   1. Ouvrir **HACS** dans le menu lateral de Home Assistant.
   2. Cliquer sur le menu **&#8942;** (trois points verticaux) en haut a droite de la page HACS, puis choisir **Depots personnalises** (*Custom repositories*).
   3. Coller l'URL du depot dans le champ **Depot** (*Repository*) : `https://github.com/cyclope205/programme-tnt-fr`
   4. Choisir **Integration** dans le menu deroulant **Type** (*Category*).
   5. Cliquer sur **Ajouter** (*Add*), puis fermer la fenetre.
2. Rechercher **Programme TNT FR** dans HACS (bouton **+ Explorer et telecharger des depots**) et l'installer.
3. Redemarrer Home Assistant.
4. Ajouter l'integration via **Parametres > Appareils et services > Ajouter une integration > Programme TNT FR**.

La carte Lovelace est enregistree automatiquement par l'integration : aucune ressource a declarer a la main.

## Configuration

A l'ajout de l'integration, une liste de chaines est proposee (les chaines de la TNT francaise sont selectionnees par defaut, une selection plus large de chaines est egalement disponible). La selection peut etre modifiee a tout moment depuis les options de l'integration, sans avoir a la reinstaller.

## Utilisation dans un tableau de bord

Ajouter une carte manuelle avec :

```yaml
type: custom:programme-tnt-fr-card
```

Aucune autre option n'est necessaire : la carte trouve elle-meme les chaines configurees.

## Attributs disponibles

Chaque capteur `sensor.programme_tnt_fr_<chaine>` expose, pour le programme `current`, `prime_time` et `second_part`, les attributs suivants :

| Attribut | Description |
| --- | --- |
| `title` | Titre du programme |
| `subtitle` | Sous-titre / episode |
| `description` | Resume |
| `category` | Categorie XMLTV |
| `icon` | Icone associee |
| `rating` | Classification (ex. age) fournie par le flux XMLTV |
| `start` / `stop` | Horaires de diffusion (ISO 8601) |
| `poster` | URL de l'affiche recuperee sur TMDB (`null` si aucune correspondance) |
| `tmdb_id` | Identifiant TMDB du film ou de la serie (`null` si aucune correspondance) |
| `tmdb_media_type` | `movie` ou `tv` selon le type de contenu (`null` si aucune correspondance) |
| `tmdb_rating` | Note moyenne TMDB, sur 10 (`0` si aucune correspondance) |
| `tmdb_votes` | Nombre de votes ayant etabli cette note (`0` si aucune correspondance) |

Exemple, pour l'attribut `prime_time` :

```yaml
prime_time:
  title: Le Fabuleux Destin d'Amelie Poulain
  subtitle: null
  category: Film
  poster: https://image.tmdb.org/t/p/w500/xxxxxx.jpg
  tmdb_id: 194
  tmdb_media_type: movie
  tmdb_rating: 7.6
  tmdb_votes: 8500
  start: "2026-08-25T21:05:00+02:00"
  stop: "2026-08-25T23:10:00+02:00"
```

Ces donnees permettent par exemple de comparer automatiquement les notes TMDB des films diffuses en prime time sur plusieurs chaines, pour ne notifier que le mieux note.

### Exemple : Top 3 films du soir (carte Markdown)

Une carte `type: markdown` standard de Home Assistant suffit a afficher un classement des films les mieux notes en 1ere partie de soiree, toutes chaines confondues :

```yaml
type: markdown
content: |
  {% set ns = namespace(films=[]) %}
  {% for entity in states.sensor | selectattr('entity_id', 'search', 'programme_tnt_fr_') | map(attribute='entity_id') | list %}
    {% set program = state_attr(entity, 'prime_time') %}
    {% if program is mapping %}
      {% set category = program.category | default('') %}
      {% set media_type = program.tmdb_media_type | default('') %}
      {% set rating = program.tmdb_rating | default(0) | float(0) %}
      {% set votes = program.tmdb_votes | default(0) | int(0) %}
      {% if category == 'Film' and media_type == 'movie' and rating > 0 %}
        {% set ns.films = ns.films + [{'title': program.title, 'channel': state_attr(entity, 'channel_name'), 'start': program.start, 'rating': rating, 'votes': votes, 'tmdb_id': program.tmdb_id}] %}
      {% endif %}
    {% endif %}
  {% endfor %}
  {% set top3 = ns.films | sort(attribute='rating', reverse=true) | list %}
  {% set medals = ['🥇', '🥈', '🥉'] %}
  ## 🏆 Top 3 films suggeres ce soir

  {% if top3 | length > 0 %}
  {% for film in top3[:3] %}
  {{ medals[loop.index0] }} **[{{ film.title }}](https://www.themoviedb.org/movie/{{ film.tmdb_id }})**

  📺 {{ film.channel }} — 🕙 {{ film.start | as_timestamp | timestamp_custom('%Hh%M', true) }} — ⭐ {{ film.rating }}/10 ({{ film.votes }} votes)

  {% endfor %}
  {% else %}
  Aucun film note trouve pour ce soir.
  {% endif %}
```

Aucune configuration necessaire : le template parcourt automatiquement tous les capteurs `programme_tnt_fr_*` presents chez l'utilisateur, quelles que soient les chaines selectionnees a la configuration. Seul le filtre `category == 'Film'` est volontaire : TMDB catalogue parfois des captations de theatre sous `tmdb_media_type: movie`, ce croisement avec la categorie XMLTV evite les faux positifs. Chaque titre est un lien direct vers sa fiche TMDB (affiche, synopsis complet, casting) : pas besoin de re-chercher le film soi-meme pour en savoir plus.
<img width="451" height="385" alt="image" src="https://github.com/user-attachments/assets/bc666b44-88ef-496e-bdc7-4ed6f4cabf75" />

## A savoir

- Le flux de programmes est actualise au maximum une fois par heure.
- La recherche d'affiches sur TMDB se fait en arriere-plan apres chaque actualisation : juste apres un redemarrage de Home Assistant, certaines vignettes peuvent afficher l'icone du flux TV le temps que TMDB reponde, puis se mettre a jour d'elles-memes.
- Les problemes et demandes d'evolution se signalent via l'onglet **Issues** du depot.

<div align="center">

### ☕ Cette intégration te plaît ?

Si elle te fait gagner du temps, un petit don est toujours apprécié : ça m'aide à maintenir le projet et à ajouter de nouvelles fonctionnalités.

<a href="https://buymeacoffee.com/cyclope205"><img src="https://img.shields.io/badge/Buy%20Me%20A%20Coffee-cyclope205-ffdd00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black" alt="Buy Me A Coffee"></a>
<a href="https://paypal.me/cyclope205"><img src="https://img.shields.io/badge/PayPal-Donate-00457C?style=for-the-badge&logo=paypal&logoColor=white" alt="PayPal"></a>

</div>
