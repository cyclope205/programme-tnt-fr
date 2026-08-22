"""Constants for the Programme TNT FR integration."""
from datetime import time

DOMAIN = "programme_tnt_fr"

# XML TV Fr - flux dedie aux chaines de la TNT francaise.
# Source et credits : https://github.com/racacax/XML-TV-Fr
XMLTV_URL = "https://xmltvfr.fr/xmltv/xmltv_tnt.xml"

CONF_CHANNELS = "channels"

# La liste complete est re-telechargee au plus une fois par heure.
# Le calcul "en ce moment / soiree" est, lui, rafraichi toutes les 5 minutes
# a partir des donnees deja en cache, sans nouvelle requete reseau.
UPDATE_INTERVAL_MINUTES = 5
FETCH_MIN_INTERVAL_MINUTES = 60

# Heuristique (heure locale) pour decouper la soiree en deux parties.
PRIME_TIME_START = time(20, 30)
LATE_NIGHT_START = time(22, 30)
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

DEFAULT_CHANNELS = [
    "TF1.fr",
    "France2.fr",
    "France3.fr",
    "France5.fr",
    "M6.fr",
    "Arte.fr",
    "W9.fr",
    "TMC.fr",
    "NT1.fr",
    "France4.fr",
    "BFMTV.fr",
    "CNews.fr",
    "Gulli.fr",
    "TF1SeriesFilms.fr",
    "6ter.fr",
    "LCI.fr",
    "FranceInfo.fr",
]
