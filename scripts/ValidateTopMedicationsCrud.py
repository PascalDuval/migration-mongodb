#!/usr/bin/env python3
"""
TopMedicationsByCancerCrud.py

Analyse CRUD (lecture simple) :
Liste les médicaments les plus prescrits aux patients atteints d’un cancer.

✅ 100 % Python (pas de pipeline MongoDB)
✅ Lecture CRUD simple avec get_collection()
✅ Option --top pour limiter le nombre de résultats
"""

import argparse
from collections import Counter
from functions_crud.crud_ops import DEFAULT_URI, DEFAULT_DB, get_collection


# === 1️⃣ Lecture CRUD et calcul Python ===
def compute_top_medications(coll, top_n=10):
    """Compte les prescriptions de médicaments pour les patients atteints de cancer."""
    # Recherche CRUD simple
    cursor = coll.find(
        {"Medical Condition": {"$regex": "Cancer", "$options": "i"}},
        {"Medication": 1, "_id": 0},
    )

    counter = Counter()
    for doc in cursor:
        med = str(doc.get("Medication", "")).strip()
        if med:
            counter[med] += 1

    if not counter:
        return []

    # Trier et limiter au top N
    results = [
        {"Medication": med, "Count": count}
        for med, count in counter.most_common(top_n)
    ]
    return results


# === 2️⃣ Affichage formaté ===
def display_results(results):
    """Affiche les résultats dans un format lisible."""
    if not results:
        print("⚠️ Aucun médicament trouvé pour les patients atteints de cancer.")
        return

    print("\n💊 Médicaments les plus prescrits pour les patients atteints de cancer :\n")
    for r in results:
        print(f"{r['Medication']}: {r['Count']} prescriptions")

    top = results[0]
    print(
        f"\n🏆 Médicament le plus prescrit : "
        f"{top['Medication']} ({top['Count']} prescriptions)"
    )


# === 3️⃣ Fonction principale ===
def main(uri: str, db_name: str, coll_name: str, top_n: int) -> int:
    print("=== 🧾 Analyse CRUD : Médicaments prescrits pour les patients atteints de cancer ===")

    coll = get_collection(uri, db_name, coll_name)
    results = compute_top_medications(coll, top_n)
    display_results(results)

    return 0


# === 4️⃣ Parsing des arguments CLI ===
def parse_args():
    parser = argparse.ArgumentParser(
        description="Lister les médicaments les plus prescrits aux patients atteints de cancer (lecture CRUD)"
    )
    parser.add_argument("--uri", default=DEFAULT_URI, help="URI MongoDB")
    parser.add_argument("--db", default=DEFAULT_DB, help="Nom de la base MongoDB")
    parser.add_argument(
        "--collection",
        default="mediccrud",
        help="Nom de la collection MongoDB (défaut : mediccrud)",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=10,
        help="Nombre de top médicaments à afficher (défaut : 10)",
    )
    return parser.parse_args()


# === 5️⃣ Point d’entrée ===
if __name__ == "__main__":
    args = parse_args()
    raise SystemExit(main(args.uri, args.db, args.collection, args.top))
