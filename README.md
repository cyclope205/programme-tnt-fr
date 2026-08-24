# Programme TNT FR

[![release](https://img.shields.io/github/v/release/cyclope205/programme-tnt-fr?label=release&color=blue)](https://github.com/cyclope205/programme-tnt-fr/releases)
[![build](https://github.com/cyclope205/programme-tnt-fr/actions/workflows/validate.yml/badge.svg)](https://github.com/cyclope205/programme-tnt-fr/actions/workflows/validate.yml)
[![license](https://img.shields.io/github/license/cyclope205/programme-tnt-fr)](LICENSE)
[![HACS: Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

<img src="https://raw.githubusercontent.com/cyclope205/programme-tnt-fr/main/custom_components/programme_tnt_fr/brand/logo.png" alt="Programme TNT FR" width="120">

Integration Home Assistant qui recupere le programme TV des chaines francaises (TNT + une selection de chaines supplementaires) et l'affiche dans une carte Lovelace : carrousel "que regarder ce soir" et guide TV complet par chaine.

## Sommaire

- [Fonctionnalites](#fonctionnalites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation dans un tableau de bord](#utilisation-dans-un-tableau-de-bord)
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

<!-- SCREENSHOT: Guide TV avec le filtre horaire -->

Un clic sur "Carrousel" dans l'entete revient a la vue de depart.

## Installation

1. Dans HACS, ajouter ce depot comme depot personnalise (categorie *Integration*) : `https://github.com/cyclope205/programme-tnt-fr`.
2. Installer **Programme TNT FR** depuis HACS.
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

## A savoir

- Le flux de programmes est actualise au maximum une fois par heure.
- La recherche d'affiches sur TMDB se fait en arriere-plan apres chaque actualisation : juste apres un redemarrage de Home Assistant, certaines vignettes peuvent afficher l'icone du flux TV le temps que TMDB reponde, puis se mettre a jour d'elles-memes.
- Les problemes et demandes d'evolution se signalent via l'onglet **Issues** du depot.
