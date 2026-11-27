**! Projet en cours de développement !**

Le but est *in fine* de *scout* les annonces Leboncoin en quête d'annonces de lots de cartes Magic intéressantes. Les conditions d'utilisation de Leboncoin interdisent l'extraction automatisée de ses annonces, donc le projet s'impose une collecte manuelle ou semi-manuelle, à faible volume.
A l'aide de machine learning, le programme permet de reconnaître les cartes à la fois grâce au texte des annonces et grâce aux images.

Version actuelle:
A partir d'un csv contenant une liste de carte, ressort les prix de ces cartes au format CSV. 
Le format d'entrée attendu est un csv contenant les colonnes: Couleur, Nom_carte, Rareté, Quantité.

Pour faire tourner le programme:
```bash
git clone https://github.com/tomsgr/lot-scout
cd lot-scout
uv sync
uv run python -m lot_scout.main chemin/vers/cartes.csv
```
Pour lancer les tests:
```bash
uv run pytest
```

