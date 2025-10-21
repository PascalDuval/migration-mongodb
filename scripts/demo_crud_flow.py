"""Demo script: insère un document dans la collection, le met à jour, puis le supprime.
Utilise `scripts.functions_crud.crud_ops.get_collection` pour la connexion.
Affiche un bilan clair (FR) et vérifie à chaque étape que l'opération a bien eu lieu.
"""
from __future__ import annotations

import argparse
import uuid
from datetime import datetime, timedelta
from bson import json_util

from scripts.functions_crud.crud_ops import get_collection, DEFAULT_URI, DEFAULT_DB, DEFAULT_COLLECTION


def main(uri: str, db_name: str, coll_name: str) -> int:
    coll = get_collection(uri, db_name, coll_name)

    # Préparer un document unique pour le test
    unique_tag = f"demo-crud-{uuid.uuid4().hex[:8]}"
    now = datetime.utcnow()
    doc = {
        "Name": "John Doe",
        "Age": 42,
        "Medication": "Ibuprofen",
        "Medical Condition": "Hypertension",
        "Blood Type": "A+",
        "Date of Admission": now,
        "Discharge Date": now,
        "note": "créé pour démonstration",
        "_demo_tag": unique_tag,
    }

    print("Étape 1/4 — insertion du document de test...")
    try:
        res = coll.insert_one(doc)
        inserted_id = res.inserted_id
        print(f"OK — document inséré avec _id: {inserted_id}")
    except Exception as e:
        print(f"ERREUR insertion : {e}")
        return 1

    # Vérifier l'existence
    found = coll.find_one({"_id": inserted_id})
    if not found:
        print("ERREUR — document introuvable après insertion")
        return 1
    print("Vérification après insertion :")
    print(json_util.dumps(found, indent=2, default=str))

    # Étape 2: mise à jour
    print("\nÉtape 2/4 — mise à jour du document (Age, Medication, Discharge Date)...")
    try:
        new_discharge = now + timedelta(days=1)
        update_doc = {"$set": {"note": "mis à jour par demo_crud_flow", "Age": 43, "Medication": "Paracetamol", "Discharge Date": new_discharge}}
        resu = coll.update_one({"_id": inserted_id}, update_doc)
        print(f"Matched: {resu.matched_count}, Modified: {resu.modified_count}")
    except Exception as e:
        print(f"ERREUR update : {e}")
        return 1

    found2 = coll.find_one({"_id": inserted_id})
    if not found2:
        print("ERREUR — document introuvable après update")
        return 1
    print("Vérification après update :")
    print(json_util.dumps(found2, indent=2, default=str))

    # Calculer et afficher le nombre de jours de prise en charge (discharge - admission)
    doa = found2.get("Date of Admission")
    dod = found2.get("Discharge Date")
    try:
        # Si ce sont des objets datetime, on peut soustraire directement
        if isinstance(doa, datetime) and isinstance(dod, datetime):
            delta = dod - doa
            days = delta.total_seconds() / 86400
            print(f"Durée de prise en charge (jours) : {days:.2f}")
        else:
            print("Impossible de calculer la durée : dates non au format datetime")
    except Exception as e:
        print(f"Erreur en calculant la durée : {e}")

    # Étape 3: suppression
    print("\nÉtape 3/4 — suppression du document de test...")
    try:
        resd = coll.delete_one({"_id": inserted_id})
        print(f"Deleted count: {resd.deleted_count}")
    except Exception as e:
        print(f"ERREUR delete : {e}")
        return 1

    # Vérifier suppression
    found3 = coll.find_one({"_id": inserted_id})
    if found3:
        print("ERREUR — document toujours présent après suppression :")
        print(json_util.dumps(found3, indent=2, default=str))
        return 1
    print("Vérification après suppression : OK — le document a bien été supprimé.")

    print("\nRésumé: toutes les étapes (insert → update → delete) se sont déroulées correctement.")
    return 0


def parse_args():
    p = argparse.ArgumentParser(description="Demo CRUD flow using functions_crud.get_collection")
    p.add_argument("--uri", default=DEFAULT_URI, help="URI MongoDB")
    p.add_argument("--db", default=DEFAULT_DB, help="Nom de la base")
    p.add_argument("--collection", default=DEFAULT_COLLECTION, help="Nom de la collection")
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    raise SystemExit(main(args.uri, args.db, args.collection))
