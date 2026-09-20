#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Valorisation d'une collection Magic à partir d'un CSV en français.

Principe :
  1. Récupère les données "bulk" de Scryfall (toutes les cartes, toutes langues),
     qui contiennent le nom imprimé FR (`printed_name`) + les prix Cardmarket en EUR.
  2. Construit deux index : nom_FR -> oracle_id  et  oracle_id -> prix EUR mini.
  3. Mappe chaque ligne de ton CSV et écrit un CSV enrichi, trié par valeur,
     puis affiche un récapitulatif (total + top cartes).

Le prix retenu = le prix EUR le plus BAS parmi toutes les éditions de la carte
(approche prudente = ce que tu encaisses en revente, hors version premium/foil).
Si une carte a une édition précise qui vaut beaucoup plus (ex: Masterpiece, Secret
Lair), il faudra la vérifier à la main — le script ne connaît pas TON édition exacte
puisqu'elle n'est pas dans le CSV.

Aucune dépendance externe : le bulk Scryfall est un fichier JSON Lines gzippé,
lu ligne par ligne en flux (sans charger ~400 Mo compressés en RAM).
Lancement :
    python valoriser_collection.py cartes_Magic_-_Feuille_1.csv
"""

import csv
import gzip
import sys
import unicodedata
import urllib.request
import json

SCRYFALL_BULK_INDEX = "https://api.scryfall.com/bulk-data"
HEADERS = {"User-Agent": "CollectionValuator/1.0", "Accept": "application/json"}


def norm(s: str) -> str:
    """Normalise un nom : minuscules, sans accents, sans ponctuation parasite."""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower().strip()
    for ch in "’'`,.!?\"":
        s = s.replace(ch, "")
    return " ".join(s.split())


def get_bulk_url() -> str:
    req = urllib.request.Request(SCRYFALL_BULK_INDEX, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    for item in data["data"]:
        if item["type"] == "all_cards":   # contient toutes les langues + prix
            return item["jsonl_download_uri"]
    raise RuntimeError("Flux 'all_cards' introuvable sur Scryfall.")


def build_indexes():
    """Stream le bulk Scryfall et construit les index nom->oracle et oracle->prix."""
    url = get_bulk_url()
    print(f"Téléchargement + lecture du bulk Scryfall (~400 Mo, une seule fois)...\n  {url}")
    fr_name_to_oracle = {}     # nom FR normalisé -> oracle_id
    en_name_to_oracle = {}     # nom EN normalisé -> oracle_id (fallback)
    oracle_to_min_eur = {}     # oracle_id -> prix EUR le plus bas trouvé

    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=120) as resp, \
            gzip.GzipFile(fileobj=resp) as gz:
        n = 0
        for line in gz:
            card = json.loads(line)
            n += 1
            if n % 50000 == 0:
                print(f"  ... {n} cartes parcourues")
            oid = card.get("oracle_id")
            if not oid:
                continue
            # Prix EUR (non foil) de cette édition
            price = (card.get("prices") or {}).get("eur")
            if price:
                try:
                    p = float(price)
                    if oid not in oracle_to_min_eur or p < oracle_to_min_eur[oid]:
                        oracle_to_min_eur[oid] = p
                except ValueError:
                    pass
            # Nom EN
            en = card.get("name")
            if en:
                en_name_to_oracle.setdefault(norm(en), oid)
            # Nom FR imprimé (présent sur les éditions lang=fr)
            if card.get("lang") == "fr":
                fr = card.get("printed_name") or card.get("name")
                if fr:
                    fr_name_to_oracle.setdefault(norm(fr), oid)
    print(f"Terminé : {n} cartes lues, "
          f"{len(fr_name_to_oracle)} noms FR, {len(oracle_to_min_eur)} prix.\n")
    return fr_name_to_oracle, en_name_to_oracle, oracle_to_min_eur


