# Programme TNT FR

<table>
<tr>
<td>

[![release](https://img.shields.io/github/v/release/cyclope205/programme-tnt-fr?label=release&color=blue)](https://github.com/cyclope205/programme-tnt-fr/releases)
[![build](https://github.com/cyclope205/programme-tnt-fr/actions/workflows/validate.yml/badge.svg)](https://github.com/cyclope205/programme-tnt-fr/actions/workflows/validate.yml)
[![license](https://img.shields.io/github/license/cyclope205/programme-tnt-fr?color=green)](LICENSE)
[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

</td>
<td width="110" align="right">
<img src="https://raw.githubusercontent.com/cyclope205/programme-tnt-fr/main/custom_components/programme_tnt_fr/brand/logo.png" width="90" alt="logo">
</td>
</tr>
</table>

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-cyclope205-ffdd00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/cyclope205)
[![PayPal](https://img.shields.io/badge/PayPal-Donate-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/cyclope205)

Intégration Home Assistant + carte Lovelace pour suivre le programme TV des
chaines de la TNT française : ce qui passe en ce moment, la première partie
de soirée et la deuxième partie de soirée, chaine par chaine, avec le détail
complet (description, genre, casting...) accessible en un clic.

**Depuis la v2.0.0**, en plus des 30 chaines de la TNT, l'integration propose
en option une soixantaine de chaines supplementaires (Canal+/Cine+, sport,
jeunesse, documentaire, musique, divertissement...), selectionnables au
meme endroit que les chaines TNT lors de la configuration.

Aucune ressource Lovelace a ajouter a la main : la carte est servie et
enregistrée automatiquement par l'intégration.

## Captures d'écran

Ecran de configuration des chaines suivies :

![Ecran de configuration des chaines suivies](https://github.com/user-attachments/assets/179cca31-8e7c-466b-b5da-8c169168f9c2)

Vue "En ce moment" / "1ere partie de soiree" avec jaquettes TMDB :

![Rendu de la carte avec jaquettes TMDB](https://github.com/user-attachments/assets/ee3804a9-a729-4b10-820b-aa1d210eba1b)

Vue "2eme partie de soirée" :

![Vue "2eme partie de soiree"](https://github.com/user-attachments/assets/39e629c2-02e7-43a5-bd89-fc73f2d7f03d)

## Fonctionnement

L'intégration récupère le flux XMLTV public de
[xmltvfr.fr](https://xmltvfr.fr) (projet
[racacax/XML-TV-Fr](https://github.com/racacax/XML-TV-Fr)), qui publie le
programme complet des chaines de la TNT française. Pour chaque chaine
sélectionnée, elle calcule :

- **En ce moment** : le programme en cours de diffusion.
- **1re partie de soirée** : le programme diffuse a partir d'environ 21h15.
- **2e partie de soirée** : le programme diffuse a partir d'environ 22h40.

Le flux complet n'est retélécharge qu'une fois par heure maximum ; le calcul
"en ce moment" est lui rafraichi toutes les 5 minutes a partir des données
déjà en cache.

Une affiche/jaquette TMDB est recherchée automatiquement pour chaque programme
(films et séries). Si aucune correspondance n'est trouvée sur TMDB, c'est
l'image du flux XMLTV (visuel de la chaine) qui est affichée a la place.

## Installation

### Via HACS (recommande)

1. Dans HACS, ouvrez le menu **...** puis **Dépôts personnalises**.
2. Ajoutez `https://github.com/cyclope205/programme-tnt-fr` avec le type
**Intégration**.
3. Installez **Programme TNT FR**, puis redémarrez Home Assistant.
4. Allez dans **Paramètres > Appareils et services > Ajouter une
intégration**, cherchez **Programme TNT FR** et choisissez les chaines a
suivre.

### Installation manuelle

Copiez le dossier `custom_components/programme_tnt_fr` dans le dossier
`custom_components` de votre configuration Home Assistant, puis
redémarrez.

## Utiliser la carte

Ajoutez une carte de type `custom:programme-tnt-fr-card` a un tableau de
bord, par exemple en mode YAML :

```yaml
type: custom:programme-tnt-fr-card
title: Programme TNT
```

Sans configuration supplementaire, la carte affiche automatiquement toutes
les chaines configurees dans l'integration. Vous pouvez aussi restreindre
l'affichage a une liste precise :

```yaml
type: custom:programme-tnt-fr-card
title: Programme TNT
entities:
- sensor.tf1
- sensor.france_2
```

Cliquez sur un programme pour ouvrir le detail (sous-titre, description,
genre, note CSA...).

## Guide TV

La carte inclut aussi une vue Guide TV façon Free, accessible via le
bouton "Guide TV" dans l'en-tete de la carte (aucune carte ni
configuration supplementaire, ca bascule simplement l'affichage) :

- **Deux chaines visibles a la fois**, avec defilement horizontal pour
en voir d'autres : au doigt sur mobile/tablette, ou avec les fleches
precedent/suivant qui apparaissent sur les cotes a la souris (PC).
- **Defilement vertical par chaine** pour parcourir tous les programmes
de la chaine au fil de la journee.
- **Recherche par chaine** : le champ en haut filtre les colonnes par
nom de chaine au fur et a mesure de la saisie.
- **Selecteur de jour** : les fleches et le libelle du jour (ex. "Lundi
24/08") permettent de consulter le programme de n'importe quel autre
jour couvert par le flux XMLTV, pas seulement aujourd'hui.
- **Filtre par horaire** : le menu a cote du selecteur de jour permet de
n'afficher que les programmes d'une plage horaire donnee (00h-06h,
06h-12h, 12h-16h, 16h-19h, 19h-21h, 21h-00h), pour retrouver rapidement
un moment de la journee sans scroller toute la liste.
- Cliquer sur un programme ouvre le meme detail (sous-titre, description,
genre...) que dans la vue carrousel.

## Modifier les chaines suivies

**Paramètres > Appareils et services > Programme TNT FR > Configurer**
permet de changer la liste des chaines a tout moment, sans réinstaller
l'integration.

## Credits

- Donnees TV : [xmltvfr.fr](https://xmltvfr.fr) / [XML TV Fr](https://github.com/racacax/XML-TV-Fr).
- Jaquettes/posters : This product uses the TMDB API but is not endorsed or certified by TMDB.
- Cette integration n'est ni affiliee ni soutenue par les chaines de
television citees.

## Licence

Voir [LICENSE](LICENSE).

## ☕ Vous aimez cette integration ?

EN - If it saves you time, consider buying me a coffee. It keeps this project maintained and new features coming.

FR - Si cette intégration te fait gagner du temps, un petit don est toujours apprécie : ca m'aide a maintenir le projet et à ajouter de nouvelles fonctionnalités.

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-cyclope205-ffdd00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/cyclope205)
[![PayPal](https://img.shields.io/badge/PayPal-Donate-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/cyclope205)
