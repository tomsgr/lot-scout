
import csv
import sys

from lot_scout.scryfall import norm
from lot_scout.scryfall import build_indexes


def main():
    if len(sys.argv) < 2:
        sys.exit("Usage : python valoriser_collection.py <fichier.csv>")
    path = sys.argv[1]
    fr_idx, en_idx, price_idx = build_indexes()

    enriched, total, non_trouvees = [], 0.0, []
    with open(path, encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)  # en-tête
        for row in reader:
            if len(row) < 4 or not row[1].strip():
                continue
            couleur, nom, rarete, qte = row[0], row[1].strip(), row[2], row[3]
            try:
                qte = int(qte)
            except (ValueError, TypeError):
                qte = 1
            key = norm(nom)
            oid = fr_idx.get(key) or en_idx.get(key)
            prix = price_idx.get(oid) if oid else None
            if prix is None:
                non_trouvees.append(nom)
                prix = 0.0
            ligne_val = prix * qte
            total += ligne_val
            enriched.append((nom, rarete, qte, round(prix, 2), round(ligne_val, 2)))

    # Tri par valeur de ligne décroissante
    enriched.sort(key=lambda x: x[4], reverse=True)

    out = "collection_valorisee.csv"
    with open(out, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Nom", "Rareté", "Qté", "Prix_min_EUR", "Valeur_ligne_EUR"])
        w.writerows(enriched)

    print("=" * 60)
    print(f"VALEUR TOTALE (somme des prix mini Cardmarket) : {total:.2f} EUR")
    print(f"Cartes non appariées : {len(non_trouvees)} "
          f"(noms FR exotiques / fautes de frappe à corriger)")
    print("=" * 60)
    print("\nTOP 25 cartes par valeur :")
    for nom, rar, qte, prix, val in enriched[:25]:
        print(f"  {val:7.2f} EUR  | {prix:6.2f} x{qte} | {rar:11} | {nom}")
    print(f"\nDétail complet écrit dans : {out}")
    if non_trouvees[:15]:
        print("\nExemples de non-appariées (à vérifier manuellement) :")
        for nm in non_trouvees[:15]:
            print("   -", nm)


if __name__ == "__main__":
    main()