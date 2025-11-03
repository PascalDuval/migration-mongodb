#!/usr/bin/env python3

import argparse
from pymongo.errors import PyMongoError
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


# === 1️⃣ Fonction d’agrégation ===
def compute_bloodtype_distribution(coll):
    """
    Exécute un pipeline d’agrégation MongoDB pour calculer la distribution
    des groupes sanguins (% de patients par type).
    """

    pipeline = [
        # Étape 1 : Ne garder que les documents ayant un groupe sanguin
        {
            "$match": {
                "Blood Type": {"$exists": True, "$ne": None}
            }
        },
        # Étape 2 : Compter le nombre d’occurrences par groupe sanguin
        {
            "$group": {
                "_id": "$Blood Type",
                "count": {"$sum": 1}
            }
        },
        # Étape 3 : Calculer le total global et empaqueter les résultats
        {
            "$group": {
                "_id": None,
                "total": {"$sum": "$count"},
                "data": {"$push": {"Blood Type": "$_id", "count": "$count"}}
            }
        },
        # Étape 4 : Déplier le tableau pour recalculer les pourcentages
        {"$unwind": "$data"},
        {
            "$project": {
                "_id": 0,
                "Blood Type": "$data.Blood Type",
                "count": "$data.count",
                "percentage": {
                    "$multiply": [{"$divide": ["$data.count", "$total"]}, 100]
                }
            }
        },
        {"$sort": {"count": -1}},
    ]

    try:
        results = list(coll.aggregate(pipeline))
        return results
    except PyMongoError as e:
        print(f"❌ Erreur MongoDB lors de l'agrégation : {e}")
        return []


# === 2️⃣ Affichage formaté des résultats ===
def display_results(results):
    """Affiche les résultats formatés, avec Pandas si disponible."""
    if not results:
        print("⚠️ Aucun résultat trouvé. Vérifie que le champ 'Blood Type' existe.")
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
        print("\n🩸 Répartition des Groupes Sanguins (CRUD) :\n")
        print(df.to_string(index=False))
    except ImportError:
        # Fallback : affichage manuel
        print("\n🩸 Répartition des Groupes Sanguins (CRUD) — mode simplifié :\n")
        for doc in results:
            bt = doc.get("Blood Type", "Inconnu")
            cnt = doc.get("count", 0)
            pct = doc.get("percentage", 0.0)
            print(f"{bt}: {cnt} ({pct:.2f}%)")


# === 3️⃣ Fonction principale ===
def main(uri: str, db_name: str, coll_name: str) -> int:
    print("=== 🧾 Analyse des Groupes Sanguins (lecture CRUD) ===")

    coll = get_collection(uri, db_name, coll_name)
    results = compute_bloodtype_distribution(coll)
    display_results(results)

    return 0


# === 4️⃣ Arguments CLI ===
def parse_args():
    parser = argparse.ArgumentParser(
        description="Calcul de la répartition des groupes sanguins (lecture CRUD)"
    )
    parser.add_argument("--uri", default=DEFAULT_URI, help="URI MongoDB")
    parser.add_argument("--db", default=DEFAULT_DB, help="Nom de la base MongoDB")
    parser.add_argument(
        "--collection",
        default=DEFAULT_COLLECTION,
        help="Nom de la collection MongoDB (défaut : mediccrud)",
    )
    return parser.parse_args()


# === 5️⃣ Point d’entrée ===
if __name__ == "__main__":
    args = parse_args()
    raise SystemExit(main(args.uri, args.db, args.collection))

