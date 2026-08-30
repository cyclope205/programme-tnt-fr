# Programme TNT FR

[![release](https://img.shields.io/github/v/release/cyclope205/programme-tnt-fr?label=release&color=blue)](https://github.com/cyclope205/programme-tnt-fr/releases)
[![build](https://github.com/cyclope205/programme-tnt-fr/actions/workflows/validate.yml/badge.svg)](https://github.com/cyclope205/programme-tnt-fr/actions/workflows/validate.yml)
[![license](https://img.shields.io/github/license/cyclope205/programme-tnt-fr)](LICENSE)
[![HACS: Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

<img src="https://raw.githubusercontent.com/cyclope205/programme-tnt-fr/main/custom_components/programme_tnt_fr/brand/logo.png" alt="Programme TNT FR" width="120">

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-cyclope205-ffdd00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/cyclope205)
[![PayPal](https://img.shields.io/badge/PayPal-Donate-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/cyclope205)

Intégration Home Assistant qui récupère le programme TV des chaines françaises (TNT + une sélection de chaines supplémentaires) et l'affiche dans une carte Lovelace : carrousel "Qu'est-ce qu'on regarde?", guide TV complet par chaine et classement des films les mieux notes.

## Sommaire

- [Fonctionnalites](#fonctionnalites)
- [Captures d'ecran](#captures-decran)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation dans un tableau de bord](#utilisation-dans-un-tableau-de-bord)
- [Attributs disponibles](#attributs-disponibles)
- [A savoir](#a-savoir)

## Fonctionnalites

-------------------------------------------------------------------------------------------------------------------------------------------------------------------
### Carrousel

Pour chaque chaîne suivie, la carte affiche jusqu'à 3 programmes : celui en cours, la premiere partie de soirée et la deuxième partie de soirée. Chaque vignette montre l'affiche du programme récupérée sur TMDB quand une correspondance fiable est trouvée, sinon l'icone fournie par le flux TV), le titre, la catégorie, la chaine et l'horaire. Un programme en cours de diffusion affiche un badge "Direct" et une barre de progression. Cliquer sur une vignette ouvre le détail du programme (synopsis, et note TMDB avec lien vers la fiche quand une correspondance est trouvée).

-------------------------------------------------------------------------------------------------------------------------------------------------------------------
**Chaines favorites** : une chaine marquée comme favorite (option `favorite_channels`) est épinglée en tête du carrousel et affiche une étoile sur ses vignettes, pour la retrouver immédiatement sans faire défiler toutes les chaines suivies.

-------------------------------------------------------------------------------------------------------------------------------------------------------------------
### Guide TV

Le bouton "Guide TV" dans l'entête de la carte bascule vers un guide complet, inspire de l'application Free : deux colonnes de chaines visibles à la fois, défilement horizontal pour changer de chaine (flèches sur ordinateur, glissement au doigt sur mobile/tablette) et défilement vertical pour parcourir la grille chronologique d'une chaine.

Le guide propose quatre filtres, combinables :
- **Recherche** : un champ texte pour ne garder que les chaines dont le nom correspond.
- **Jour** : flèches précédente/suivant pour changer de journée de diffusion.
- **Horaire** : un menu pour n'afficher que les programmes d'une plage donnée (00h-06h, 06h-12h, 12h-16h, 16h-19h, 19h-21h, 21h-00h), pour retrouver rapidement un moment de la journée sans faire défiler toute la liste.
- **Genre** : un menu pour ne garder que les programmes d'un type donne (Film, Série, Sport, etc.).

Un clic sur "Carrousel" dans l'entête revient a la vue de départ.

-------------------------------------------------------------------------------------------------------------------------------------------------------------------
### Top films

Un bouton dans l'entête de la carte ouvre le classement des films les mieux notes (TMDB) en 1ere partie de soirée, navigable jour par jour sur environ une semaine — la même logique que la carte markdown ci-dessous, mais sans se limiter au soir même.

-------------------------------------------------------------------------------------------------------------------------------------------------------------------
## Captures d'ecran

Ecran de configuration des chaines suivies :

![Ecran de configuration des chaines suivies](https://github.com/user-attachments/assets/179cca31-8e7c-466b-b5da-8c169168f9c2)

-------------------------------------------------------------------------------------------------------------------------------------------------------------------
Vue "En ce moment" / "1ere partie de soirée" avec jaquettes TMDB :

![Rendu de la carte avec jaquettes TMDB](https://github.com/user-attachments/assets/ee3804a9-a729-4b10-820b-aa1d210eba1b)

-------------------------------------------------------------------------------------------------------------------------------------------------------------------
Vue "2eme partie de soirée" :

![Vue 2eme partie de soiree](https://github.com/user-attachments/assets/39e629c2-02e7-43a5-bd89-fc73f2d7f03d)

-------------------------------------------------------------------------------------------------------------------------------------------------------------------
Guide TV, avec le "filtre horaire" :

<img width="184" height="320" alt="Capture d-ecran 2026-08-26 a 22 09 20" src="https://github.com/user-attachments/assets/c32927eb-80a2-4eba-b5c5-d9c87cb4be66" />


-------------------------------------------------------------------------------------------------------------------------------------------------------------------
Configuration des chaines favorites:

<img width="1286" height="812" alt="image" src="https://github.com/user-attachments/assets/9625d200-f72b-44ee-9e38-63572ff7416e" />

-------------------------------------------------------------------------------------------------------------------------------------------------------------------
Carrousel avec une chaine favorite épinglée et son étoile:

<img width="1271" height="777" alt="image" src="https://github.com/user-attachments/assets/b705a916-4f02-4c8c-bc93-4062756b2231" />

-------------------------------------------------------------------------------------------------------------------------------------------------------------------
Guide TV avec le filtre "Genre" appliqué:

<img width="184" height="320" alt="Capture d-ecran 2026-08-26 a 22 08 04" src="https://github.com/user-attachments/assets/95a1fffc-ad10-49c1-a3d2-ae9cf68a7758" />

-------------------------------------------------------------------------------------------------------------------------------------------------------------------
Vue Top films avec la navigation jour par jour:

<img width="460" height="552" alt="image" src="https://github.com/user-attachments/assets/53121b73-6221-4704-b054-36fe7cdcc835" />

-------------------------------------------------------------------------------------------------------------------------------------------------------------------
## Installation

1. Ajouter ce depot a HACS comme depot personnalise :
   1. Ouvrir **HACS** dans le menu latéral de Home Assistant.
   2. Cliquer sur le menu **&#8942;** (trois points verticaux) en haut a droite de la page HACS, puis choisir **Dépôts personnalisés** (*Custom repositories*).
   3. Coller l'URL du depot dans le champ **Dépôt** (*Repository*) : `https://github.com/cyclope205/programme-tnt-fr`
   4. Choisir **Integration** dans le menu deroulant **Type** (*Category*).
   5. Cliquer sur **Ajouter** (*Add*), puis fermer la fenetre.
2. Rechercher **Programme TNT FR** dans HACS (bouton **+ Explorer et télécharger des dépôts**) et l'installer.
3. Redémarrer Home Assistant.
4. Ajouter l'integration via **Paramètres > Appareils et services > Ajouter une intégration > Programme TNT FR**.

La carte Lovelace est enregistrée automatiquement par l'intégration : aucune ressource a déclarer à la main.

-------------------------------------------------------------------------------------------------------------------------------------------------------------------
## Configuration

A l'ajout de l'intégration, une liste de chaines est proposée (les chaines de la TNT francaise sont selectionnées par defaut, une selection plus large de chaines est également disponible). La selection peut être modifiée à tout moment depuis les options de l'intégration, sans avoir à la réinstaller.

Les chaines favorites se choisissent également depuis les options de l'intégration : cette sélection est facultative et n'affecte que l'ordre d'affichage dans le carrousel.

-------------------------------------------------------------------------------------------------------------------------------------------------------------------
## Utilisation dans un tableau de bord

Ajouter une carte manuelle avec :

```yaml
type: custom:programme-tnt-fr-card
```

Aucune autre option n'est nécessaire : la carte trouve elle-même les chaines configurées.

-------------------------------------------------------------------------------------------------------------------------------------------------------------------
### Options d'affichage

Par défaut, les trois sections (En ce moment / 1ere partie de soirée / 2eme partie de soirée) sont toutes affichées. Chacune peut être masquée individuellement avec les options suivantes (toutes à `true` par defaut) :

```yaml
type: custom:programme-tnt-fr-card
show_current: true
show_prime_time: true
show_second_part: true
```

Ces options sont également disponibles directement dans l'éditeur visuel de la carte (trois interrupteurs), pas seulement en YAML : ouvrez l'édition de la carte depuis le tableau de bord, l'éditeur graphique propose les trois bascules sans avoir a écrire de YAML.

Les trois vues de la carte (Carrousel, Guide TV, Top films) peuvent elles aussi être masquées individuellement, avec les options suivantes (toutes à `true` par défaut) :

```yaml
type: custom:programme-tnt-fr-card
show_carousel: true
show_guide_tv: true
show_top_films: true
```

Ces trois bascules sont également disponibles dans l'éditeur visuel, sous "Vues disponibles". Les boutons de navigation dans l'entête ne s'affichent que si plusieurs vues sont actives à la fois ; si une seule vue reste activée, la carte l'affiche directement sans bouton de navigation (utile par exemple pour n'afficher que le Guide TV sur un écran dédié).

Par exemple, pour masquer uniquement le programme "en ce moment" (comme sur la capture ci-dessous) :

```yaml
type: custom:programme-tnt-fr-card
show_current: false
```
<img width="1277" height="790" alt="image" src="https://github.com/user-attachments/assets/562f46bf-67ed-40b6-8159-4aa55b25fd33" />

Les chaines favorites, épinglées en tête du carrousel avec une étoile, se configurent avec `favorite_channels` :

```yaml
type: custom:programme-tnt-fr-card
favorite_channels:
  - TF1
  - France 2
```

Comme pour les trois bascules `show_*`, cette option est aussi accessible depuis l'éditeur visuel de la carte, sans avoir à écrire de YAML.

-------------------------------------------------------------------------------------------------------------------------------------------------------------------
## Attributs disponibles

Chaque capteur `sensor.programme_tnt_fr_<chaine>` éxpose, pour le programme `current`, `prime_time` et `second_part`, les attributs suivants :

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

Ces données permettent par exemple de comparer automatiquement les notes TMDB des films diffusés en prime time sur plusieurs chaines, pour ne notifier que le mieux noté.

-------------------------------------------------------------------------------------------------------------------------------------------------------------------
### Exemple : Top 3 films du soir (carte Markdown)

Une carte `type: markdown` standard de Home Assistant suffit à afficher un classement des films les mieux notes en 1ere partie de soirée, toutes chaines confondues. Le titre du classement reprend désormais le nombre réel de films trouvés :

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
        {% set ns.films = ns.films + [{'title': program.title, 'channel': state_attr(entity, 'channel_name'), 'start': program.start, 'rating': rating, 'votes': votes, 'tmdb_id': program.tmdb_id, 'poster': program.poster}] %}
      {% endif %}
    {% endif %}
  {% endfor %}
  {% set top3 = ns.films | sort(attribute='rating', reverse=true) | list %}
  {% set displayed = top3[:3] %}
  {% set medals = ['🥇', '🥈', '🥉'] %}
  ## 🏆 Top {{ displayed | length }} film{{ 's' if displayed | length > 1 else '' }} suggér{{ 'és' if displayed | length > 1 else 'é' }} ce soir (1ère partie de soirée)
  {% if displayed | length > 0 %}
  {% for film in displayed %}
  {{ medals[loop.index0] }}{% if film.poster %} <img src="{{ film.poster }}" width="40" style="vertical-align:middle;border-radius:4px;margin-right:4px;">{% endif %} **[{{ film.title }}](https://www.themoviedb.org/movie/{{ film.tmdb_id }})**

  📺 {{ film.channel }} — 🕘 {{ film.start | as_timestamp | timestamp_custom('%Hh%M', true) }} — ⭐ {{ film.rating }}/10 ({{ film.votes }} votes)

  {% endfor %}
  {% else %}
  Aucun film noté trouvé pour ce soir.
  {% endif %}
```

Aucune configuration nécessaire : le Template parcourt automatiquement tous les capteurs `programme_tnt_fr_*` présents chez l'utilisateur, quelles que soient les chaines sélectionnées à la configuration. Seul le filtre `category == 'Film'` est volontaire : TMDB catalogue parfois des captations de théâtre sous `tmdb_media_type: movie`, ce croisement avec la catégorie XMLTV évite les faux positifs. Chaque titre est un lien direct vers sa fiche TMDB (affiche, synopsis complet, casting) : pas besoin de re-chercher le film soi-même pour en savoir plus. Le titre du classement (`{{ displayed | length }}`) reflète désormais le nombre réel de films trouves, plutôt que d'afficher systématiquement "Top 3" même quand moins de films correspondent. La jaquette TMDB du film s'affiche désormais devant chaque titre, quand une correspondance est trouvée.

<img width="451" height="385" alt="image" src="https://github.com/user-attachments/assets/bc666b44-88ef-496e-bdc7-4ed6f4cabf75" />

-------------------------------------------------------------------------------------------------------------------------------------------------------------------
## A savoir

- Le flux de programmes est actualise au maximum une fois par heure.
- La recherche d'affiches sur TMDB se fait en arrière-plan après chaque actualisation : juste après un redémarrage de Home Assistant, certaines vignettes peuvent afficher l'icone du flux TV le temps que TMDB réponde, puis se mettre a jour d'elles-mêmes. Cela peut entrainer un temps de chargement qui affiche un message d'erreur de configuration. En patientant un court moment et en actualisant éventuellement la page ou la vue, celle-ci apparaitra.
- Toutes les nouvelles options (`favorite_channels`, filtre Genre, vue Top films, `show_carousel`/`show_guide_tv`/`show_top_films`) sont facultatives : le comportement par défaut de la carte reste inchangé pour les configurations existantes.
- La carte se protège désormais contre un double enregistrement du composant (garde `customElements.get()` avant `customElements.define()`), une cause possible de l'erreur "Custom element doesn't exist" rapportée occasionnellement par certains utilisateurs.
- Le fichier JS de la carte est servi sans en-tete de cache HTTP explicite (`cache_headers=False`), pour reduire le risque que le navigateur garde en memoire une ancienne version de la carte apres une mise a jour. Si la carte ne se met pas a jour visuellement apres une mise a jour HACS (redemarrage effectue), un rechargement force de la page (ou de l'application Compagnon) resout generalement le probleme.
- Les problèmes et demandes d'évolution se signalent via l'onglet **Issues** du dépôt.
<div align="center">

-------------------------------------------------------------------------------------------------------------------------------------------------------------------
### ☕ Cette intégration te plaît ?

Si elle te fait gagner du temps, un petit don est toujours apprécié : ça m'aide à maintenir le projet et à ajouter de nouvelles fonctionnalités.

<a href="https://buymeacoffee.com/cyclope205"><img src="https://img.shields.io/badge/Buy%20Me%20A%20Coffee-cyclope205-ffdd00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black" alt="Buy Me A Coffee"></a>
<a href="https://paypal.me/cyclope205"><img src="https://img.shields.io/badge/PayPal-Donate-00457C?style=for-the-badge&logo=paypal&logoColor=white" alt="PayPal"></a>

</div>
