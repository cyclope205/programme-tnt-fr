"""Constants for the Programme TNT FR integration."""
from datetime import time

DOMAIN = "programme_tnt_fr"

# XML TV Fr - flux dedie aux chaines de la TNT francaise.
# Source et credits : https://github.com/racacax/XML-TV-Fr
XMLTV_URL = "https://xmltvfr.fr/xmltv/xmltv_tnt.xml"

CONF_CHANNELS = "channels"

# Cle API TMDB (The Movie Database) optionnelle : si renseignee, l'integration
# tente de recuperer une affiche officielle (films et series) pour chaque
# programme via l'API publique TMDB, en complement de l'image fournie par le
# flux XMLTV (qui n'est pas toujours une vraie jaquette). Facultatif : sans
# cle, le comportement precedent (image du flux XMLTV) est inchange.
CONF_TMDB_API_KEY = "tmdb_api_key"
TMDB_SEARCH_MOVIE_URL = "https://api.themoviedb.org/3/search/movie"
TMDB_SEARCH_TV_URL = "https://api.themoviedb.org/3/search/tv"
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

# Cle TMDB partagee par defaut : cela evite a chaque utilisateur de devoir
# creer un compte TMDB pour profiter des jaquettes. Usage strictement non
# commercial (voir la section Credits du README pour attribution requise
# par TMDB). Les utilisateurs qui le souhaitent peuvent renseigner leur
# propre cle dans les options de integration : celle-ci a alors priorite.
DEFAULT_TMDB_API_KEY = "3180ede1f0ea4c773b9d54f45020143c"

# La liste complete est re-telechargee au plus une fois par heure.
# Le calcul "en ce moment / soiree" est, lui, rafraichi toutes les 5 minutes
# a partir des donnees deja en cache, sans nouvelle requete reseau.
UPDATE_INTERVAL_MINUTES = 5
FETCH_MIN_INTERVAL_MINUTES = 60

# Heuristique (heure locale) pour decouper la soiree en deux parties : on
# cherche le programme diffuse a cet instant precis, et seulement si aucun
# programme ne couvre cet instant (ex: coupure pub) on prend le premier qui
# demarre juste apres. Cela evite qu'un tres court programme de transition
# (bande-annonce, interstitiel de quelques minutes) ne soit choisi a la
# place du programme vedette de la soiree.
PRIME_TIME_START = time(21, 15)
LATE_NIGHT_START = time(22, 40)
DAY_RESET = time(5, 0)

# Chaines standard de la TNT francaise telles que publiees par xmltvfr.fr
# (https://xmltvfr.fr/channels.php?guide=tnt). Cle = identifiant XMLTV du
# flux, valeur = nom convivial affiche dans Home Assistant.
TNT_CHANNELS = {
    "TF1.fr": "TF1",
    "France2.fr": "France 2",
    "France3.fr": "France 3",
    "CanalPlus.fr": "Canal+",
    "France5.fr": "France 5",
    "M6.fr": "M6",
    "Arte.fr": "Arte",
    "W9.fr": "W9",
    "TMC.fr": "TMC",
    "NT1.fr": "TFX",
    "LaChaineParlementaire.fr": "LCP",
    "France4.fr": "France 4",
    "BFMTV.fr": "BFM TV",
    "CNews.fr": "CNews",
    "CStar.fr": "CStar",
    "Gulli.fr": "Gulli",
    "T18.fr": "T18",
    "NOVO19.fr": "NOVO19",
    "TF1SeriesFilms.fr": "TF1 Series Films",
    "LEquipe21.fr": "L'Equipe",
    "6ter.fr": "6ter",
    "Numero23.fr": "RMC Story",
    "RMCDecouverte.fr": "RMC Decouverte",
    "Cherie25.fr": "RMC Life",
    "LCI.fr": "LCI",
    "FranceInfo.fr": "franceinfo",
    "ParisPremiere.fr": "Paris Premiere",
    "CanalPlusSport.fr": "Canal+ Sport",
    "CanalPlusCinema.fr": "Canal+ Cinema",
    "PlanetePlus.fr": "Planete+",
}

# Par defaut, l'integration suit TOUTES les chaines de la liste ci-dessus.
DEFAULT_CHANNELS = list(TNT_CHANNELS.keys())
