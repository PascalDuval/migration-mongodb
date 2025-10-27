#!/usr/bin/env python3
"""
Durée moyenne des séjours hospitaliers (lecture CRUD).
Ce script lit les documents contenant "Date of Admission" et "Discharge Date"
dans une collection MongoDB, calcule la durée du séjour en jours côté Python,
et affiche un résumé statistique simple.

✅ Compatibilité :
- Dates stockées comme datetime dans MongoDB (type `date`)
- Dates stockées comme chaînes ISO (ex: "2024-05-10T00:00:00" ou "2024-05-10")
"""

import argparse
from datetime import datetime
from statistics import mean

from pymongo.collection import Collection
from pymongo.errors import PyMongoError

# 🔧 Import du module CRUD (adapter selon ton arborescence)
from functions_crud.crud_ops import DEFAULT_DB, DEFAULT_URI, get_collection


# === 1️⃣ Extraction des durées ===
def load_durations(coll: Collection) -> list[float]:
    """Retourne les durées de séjour valides (en jours décimaux)."""

    # 🔍 On ne filtre plus par "$type: date" pour ne pas exclure les chaînes
    filter_query = {
        "Date of Admission": {"$exists": True},
        "Discharge Date": {"$exists": True},
    }
    projection = {"Date of Admission": 1, "Discharge Date": 1}

    try:
        cursor = coll.find(filter_query, projection)
    except PyMongoError as exc:
        print(f"❌ Erreur MongoDB lors de la lecture : {exc}")
        return []

    durations: list[float] = []

    for doc in cursor:
        start = doc.get("Date of Admission")
        end = doc.get("Discharge Date")

        # 🧩 Conversion auto des chaînes ISO en datetime
        start = convert_to_datetime(start)
        end = convert_to_datetime(end)

        # ⛔ Si l'une des dates est invalide ou inversée, on ignore
        if not start or not end or end < start:
            continue

        # ✅ Calcul en jours
        duration_days = (end - start).total_seconds() / 86400.0
        durations.append(duration_days)

    print(f"✅ {len(durations)} séjours valides calculés.")
    return durations


# === 2️⃣ Conversion universelle ===
def convert_to_datetime(value):
    """Convertit un champ MongoDB en datetime Python si possible."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        # Essaie plusieurs formats courants
        for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
            try:
                return datetime.strptime(value.strip(), fmt)
            except ValueError:
                continue
    return None


# === 3️⃣ Résumé des résultats ===
def show_summary(durations: list[float]) -> None:
    """Affiche un résumé simple des statistiques calculées."""
    if not durations:
        print("⚠️ Aucun séjour valide trouvé (dates manquantes ou incohérentes).")
        return

    durations.sort()
    print("\n🏥 Durée moyenne des séjours hospitaliers :\n")
    print(f"Nombre de séjours analysés : {len(durations)}")
    print(f"Durée moyenne : {mean(durations):.2f} jours")
    print(f"Durée minimale : {durations[0]:.2f} jours")
    print(f"Durée médiane : {durations[len(durations)//2]:.2f} jours")
    print(f"Durée maximale : {durations[-1]:.2f} jours")


# === 4️⃣ Fonction principale ===
def main(uri: str, db_name: str, coll_name: str) -> int:
    print("=== 🧾 Calcul de la durée moyenne des séjours hospitaliers ===")
    coll = get_collection(uri, db_name, coll_name)

    # Affiche un exemple de document pour contrôle
    example = coll.find_one({}, {"Date of Admission": 1, "Discharge Date": 1})
    print(f"🧾 Exemple de document : {example}")

    durations = load_durations(coll)
    show_summary(durations)
    return 0


# === 5️⃣ Parsing des arguments CLI ===
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Calcul de la durée moyenne de séjour (lecture CRUD)",
    )
    parser.add_argument("--uri", default=DEFAULT_URI, help="URI MongoDB")
    parser.add_argument("--db", default=DEFAULT_DB, help="Nom de la base MongoDB")
    parser.add_argument(
        "--collection",
        default="mediccrud",
        help="Nom de la collection MongoDB (défaut : mediccrud)",
    )
    return parser.parse_args()


# === 6️⃣ Point d'entrée ===
if __name__ == "__main__":
    args = parse_args()
    raise SystemExit(main(args.uri, args.db, args.collection))
