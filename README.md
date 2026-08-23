# Programme TNT FR

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-cyclope205-ffdd00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/cyclope205)
[![PayPal](https://img.shields.io/badge/PayPal-Donate-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/cyclope205)

Integration Home Assistant + carte Lovelace pour suivre le programme TV des
chaines de la TNT francaise : ce qui passe en ce moment, la premiere partie
de soiree et la deuxieme partie de soiree, chaine par chaine, avec le detail
complet (description, genre, casting...) accessible en un clic.

Aucune ressource Lovelace a ajouter a la main : la carte est servie et
enregistree automatiquement par l'integration.

## Captures d'ecran

Ecran de configuration des chaines suivies :

![Ecran de configuration des chaines suivies](https://github.com/user-attachments/assets/179cca31-8e7c-466b-b5da-8c169168f9c2)

Vue "En ce moment" / "1ere partie de soiree" avec jaquettes TMDB :

![Rendu de la carte avec jaquettes TMDB](https://github.com/user-attachments/assets/ee3804a9-a729-4b10-820b-aa1d210eba1b)

## Fonctionnement

L'integration recupere le flux XMLTV public de
[xmltvfr.fr](https://xmltvfr.fr) (projet
[racacax/XML-TV-Fr](https://github.com/racacax/XML-TV-Fr)), qui publie le
programme complet des chaines de la TNT francaise. Pour chaque chaine
selectionnee, elle calcule :

- **En ce moment** : le programme en cours de diffusion.
- **1re partie de soiree** : le programme diffuse a partir d'environ 21h15.
- **2e partie de soiree** : le programme diffuse a partir d'environ 22h40.

Le flux complet n'est retelecharge qu'une fois par heure maximum ; le calcul
"en ce moment" est lui rafraichi toutes les 5 minutes a partir des donnees
deja en cache.

## Installation

### Via HACS (recommande)

1. Dans HACS, ouvrez le menu **...** puis **Depots personnalises**.
2. Ajoutez `https://github.com/cyclope205/programme-tnt-fr` avec le type
**Integration**.
3. Installez **Programme TNT FR**, puis redemarrez Home Assistant.
4. Allez dans **Parametres > Appareils et services > Ajouter une
integration**, cherchez **Programme TNT FR** et choisissez les chaines a
suivre.

### Installation manuelle

Copiez le dossier `custom_components/programme_tnt_fr` dans le dossier
`custom_components` de votre configuration Home Assistant, puis
redemarrez.

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

## Modifier les chaines suivies

**Parametres > Appareils et services > Programme TNT FR > Configurer**
permet de changer la liste des chaines a tout moment, sans reinstaller
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

FR - Si cette integration te fait gagner du temps, un petit don est toujours apprecie : ca m'aide a maintenir le projet et a ajouter de nouvelles fonctionnalites.

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-cyclope205-ffdd00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/cyclope205)
[![PayPal](https://img.shields.io/badge/PayPal-Donate-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/cyclope205)
