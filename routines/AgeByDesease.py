#!/usr/bin/env python3

import argparse
from collections import defaultdict
from statistics import mean

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from functions_crud.crud_ops import DEFAULT_URI, DEFAULT_DB, get_collection


# === 1️⃣ Lecture CRUD et calcul Python ===
def compute_average_age_by_condition(coll):
    """Calcule l’âge moyen (arrondi) par pathologie à partir des documents MongoDB."""

    cursor = coll.find(
        {
            "Age": {"$exists": True, "$ne": None, "$ne": ""},
            "Medical Condition": {"$exists": True, "$ne": None, "$ne": ""},
        },
        {"Age": 1, "Medical Condition": 1, "_id": 0},
    )

    ages_by_condition = defaultdict(list)

    for doc in cursor:
        try:
            age = int(doc.get("Age"))
        except (ValueError, TypeError):
            continue  # on ignore les valeurs non convertibles

        condition = str(doc.get("Medical Condition", "")).strip()
        if not condition:
            continue

        ages_by_condition[condition].append(age)

    if not ages_by_condition:
        return []

    # Calcul de l'âge moyen arrondi pour chaque pathologie
    results = []
    for cond, ages in ages_by_condition.items():
        avg_age = round(mean(ages))
        results.append(
            {
                "Pathologie": cond,
                "Âge Moyen": avg_age,
                "Nombre de Patients": len(ages),
            }
        )

    # Tri décroissant par âge moyen
    results.sort(key=lambda x: x["Âge Moyen"], reverse=True)
    return results


# === 2️⃣ Affichage formaté ===
def display_results(results):
    """Affiche les résultats avec Pandas si possible, sinon en mode texte."""
    if not results:
        print("⚠️ Aucune donnée d'âge trouvée pour les pathologies.")
        return

    try:
        import pandas as pd
        df = pd.DataFrame(results)
        print("\n📊 Âge moyen (arrondi) des patients selon les pathologies :\n")
        print(df.to_string(index=False))
    except ImportError:
        print("\n📊 Âge moyen (arrondi) des patients selon les pathologies (mode texte) :\n")
        for r in results:
            print(
                f"{r['Pathologie']}: Âge moyen {r['Âge Moyen']} ans "
                f"({r['Nombre de Patients']} patients)"
            )


# === 3️⃣ Fonction principale ===
def main(uri: str, db_name: str, coll_name: str) -> int:
    print("=== 🧾 Analyse CRUD : Âge moyen des patients par pathologie ===")

    coll = get_collection(uri, db_name, coll_name)
    results = compute_average_age_by_condition(coll)
    display_results(results)

    return 0


# === 4️⃣ Parsing des arguments CLI ===
def parse_args():
    parser = argparse.ArgumentParser(
        description="Calcule l'âge moyen (arrondi) des patients selon la pathologie (lecture CRUD)"
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
