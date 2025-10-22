#!/usr/bin/env python3
"""
BloodTypeDistributionCrud.py

Analyse CRUD (lecture simple) de la répartition des groupes sanguins
dans la base MongoDB.

Pour chaque groupe sanguin :
  - Nombre total de patients
  - Pourcentage du total

Implémenté 100 % côté Python, sans pipeline d’agrégation MongoDB.

Usage :
  python scripts/BloodTypeDistributionCrud.py
  ou
  python scripts/BloodTypeDistributionCrud.py --db FirstTry --collection medic2
"""

import argparse
from collections import Counter

from pymongo.errors import PyMongoError
from functions_crud.crud_ops import DEFAULT_URI, DEFAULT_DB, get_collection


# === 1️⃣ Lecture CRUD et calcul côté Python ===
def compute_bloodtype_distribution(coll):
    """Calcule la distribution des groupes sanguins à partir des documents MongoDB."""
    try:
        # Lecture CRUD simple
        cursor = coll.find({"Blood Type": {"$exists": True, "$ne": None}}, {"Blood Type": 1})
    except PyMongoError as exc:
        print(f"❌ Erreur MongoDB lors de la lecture : {exc}")
        return []

    counter = Counter()
    total = 0

    for doc in cursor:
        blood_type = str(doc.get("Blood Type", "Inconnu")).strip()
        if not blood_type:
            continue
        counter[blood_type] += 1
        total += 1

    if total == 0:
        return []

    # Préparer les résultats sous forme de liste de dictionnaires
    results = [
        {
            "Blood Type": bt,
            "count": count,
            "percentage": (count / total) * 100,
        }
        for bt, count in sorted(counter.items(), key=lambda x: x[1], reverse=True)
    ]
    return results


# === 2️⃣ Affichage formaté ===
def display_results(results):
    """Affiche les résultats avec pandas si disponible, sinon en texte brut."""
    if not results:
        print("⚠️ Aucun groupe sanguin trouvé dans la collection.")
        return

    try:
        import pandas as pd
        df = pd.DataFrame(results)
        df.rename(
            columns={
                "Blood Type": "Groupe Sanguin",
                "count": "Nombre de Patients",
                "percentage": "Pourcentage",
            },
            inplace=True,
        )
        df["Pourcentage"] = df["Pourcentage"].map("{:.2f}%".format)
        print("\n🩸 Répartition des Groupes Sanguins (CRUD Python) :\n")
        print(df.to_string(index=False))
    except ImportError:
        print("\n🩸 Répartition des Groupes Sanguins (CRUD Python) — mode texte :\n")
        for r in results:
            print(f"{r['Blood Type']}: {r['count']} ({r['percentage']:.2f}%)")


# === 3️⃣ Fonction principale ===
def main(uri: str, db_name: str, coll_name: str) -> int:
    print("=== 🧾 Analyse CRUD des Groupes Sanguins ===")

    coll = get_collection(uri, db_name, coll_name)
    results = compute_bloodtype_distribution(coll)
    display_results(results)

    return 0


# === 4️⃣ Parsing des arguments CLI ===
def parse_args():
    parser = argparse.ArgumentParser(
        description="Calcul de la répartition des groupes sanguins (lecture CRUD)"
    )
    parser.add_argument("--uri", default=DEFAULT_URI, help="URI MongoDB")
    parser.add_argument("--db", default=DEFAULT_DB, help="Nom de la base MongoDB")
    parser.add_argument(
        "--collection",
        default="mediccrud",
        help="Nom de la collection MongoDB (défaut : mediccrud)",
    )
    return parser.parse_args()


# === 5️⃣ Point d’entrée ===
if __name__ == "__main__":
    args = parse_args()
    raise SystemExit(main(args.uri, args.db, args.collection))
