#!/usr/bin/env python3


import argparse
from collections import Counter
from functions_crud.crud_ops import DEFAULT_URI, DEFAULT_DB, get_collection


# === 1️⃣ Lecture CRUD et calcul côté Python ===
def compute_top_hospitals(coll):
    """Compte le nombre d’admissions par hôpital et retourne le classement."""
    cursor = coll.find({"Hospital": {"$exists": True, "$ne": None}}, {"Hospital": 1})

    counter = Counter()
    for doc in cursor:
        hospital = str(doc.get("Hospital", "")).strip()
        if hospital:
            counter[hospital] += 1

    if not counter:
        return []

    # Transformer en liste triée
    results = [
        {"Hospital": name, "Admissions": count}
        for name, count in counter.most_common()
    ]
    return results


# === 2️⃣ Affichage des résultats ===
def display_results(results):
    """Affiche le top 1 et un aperçu des hôpitaux."""
    if not results:
        print("⚠️ Aucun hôpital trouvé dans la base de données.")
        return

    print("\n🏥 Classement des hôpitaux selon les admissions :\n")
    for r in results[:10]:  # n’affiche que le top 10
        print(f"{r['Hospital']}: {r['Admissions']} admissions")

    top = results[0]
    print(
        f"\n🏆 Hôpital avec le plus d'admissions : "
        f"{top['Hospital']} ({top['Admissions']} admissions)"
    )


# === 3️⃣ Fonction principale ===
def main(uri: str, db_name: str, coll_name: str) -> int:
    print("=== 🧾 Analyse CRUD : Admissions par hôpital ===")

    coll = get_collection(uri, db_name, coll_name)
    results = compute_top_hospitals(coll)
    display_results(results)

    return 0


# === 4️⃣ Parsing des arguments CLI ===
def parse_args():
    parser = argparse.ArgumentParser(
        description="Trouver l’hôpital ayant le plus d’admissions (lecture CRUD)"
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
