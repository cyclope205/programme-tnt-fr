# Programme TNT FR

Integration Home Assistant + carte Lovelace pour suivre le programme TV des
chaines de la TNT francaise : ce qui passe en ce moment, la premiere partie
de soiree et la deuxieme partie de soiree, chaine par chaine, avec le detail
complet (description, genre, casting...) accessible en un clic.

Aucune ressource Lovelace a ajouter a la main : la carte est servie et
enregistree automatiquement par l'integration.

## Fonctionnement

L'integration recupere le flux XMLTV public de
[xmltvfr.fr](https://xmltvfr.fr) (projet
[racacax/XML-TV-Fr](https://github.com/racacax/XML-TV-Fr)), qui publie le
programme complet des chaines de la TNT francaise. Pour chaque chaine
selectionnee, elle calcule :

- **En ce moment** : le programme en cours de diffusion.
- **1re partie de soiree** : le programme diffuse a partir d'environ 20h30.
- **2e partie de soiree** : le programme diffuse a partir d'environ 22h30.

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
- Cette integration n'est ni affiliee ni soutenue par les chaines de
  television citees.

## Licence

MIT, voir [LICENSE](LICENSE).
