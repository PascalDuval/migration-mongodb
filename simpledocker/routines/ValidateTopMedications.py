#!/usr/bin/env python3


import argparse
from collections import Counter
import os
from urllib.parse import quote_plus
from pymongo import MongoClient

# Defaults via environment for Docker/Compose
_URI_ENV = (
    os.getenv("MONGO_URI")
    or os.getenv("MIGRATION_MONGODB_URI")
    or os.getenv("MONGODB_URI")
)
DEFAULT_DB = os.getenv("MONGO_DB", "FirstTry")
DEFAULT_COLLECTION = os.getenv("MONGO_COLLECTION", "mediccrud")
HOST = os.getenv("MONGO_HOST", "mongodb")

def _build_uri(db: str) -> str:
    if _URI_ENV:
        return _URI_ENV
    user = os.getenv("MONGO_APP_USERNAME")
    pwd = os.getenv("MONGO_APP_PASSWORD")
    if user and pwd:
        return f"mongodb://{quote_plus(user)}:{quote_plus(pwd)}@{HOST}:27017/{db}?authSource={db}"
    return f"mongodb://{HOST}:27017"


def get_collection(uri: str, db_name: str, coll_name: str):
    eff_uri = uri or _build_uri(db_name)
    client = MongoClient(eff_uri)
    return client[db_name][coll_name]


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
        default=DEFAULT_COLLECTION,
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

