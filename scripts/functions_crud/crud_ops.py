from typing import Any, Dict, List, Optional
from pathlib import Path
from datetime import datetime
import pandas as pd
import pymongo
from pymongo import MongoClient
from bson import json_util, ObjectId

from .convert import _safe_int, _to_datetime, convert_dataframe_types


DEFAULT_URI = "mongodb://localhost:27017"
DEFAULT_DB = "FirstTry"
DEFAULT_COLLECTION = "mediccrud"


def get_collection(uri: str, db_name: str, coll_name: str):
    client = MongoClient(uri)
    db = client[db_name]
    return db[coll_name]


def import_csv(uri: str, db: str, collection: str, file: str, batch_size: int = 1000, dry_run: bool = False):
    coll = get_collection(uri, db, collection)

    candidates = [Path(file), Path(__file__).parent.joinpath(file), Path.cwd().joinpath(file), Path.cwd().joinpath("data", Path(file).name), Path(__file__).parent.parent.joinpath("data", Path(file).name)]

    path = None
    for c in candidates:
        if c.exists():
            path = c
            break

    if path is None:
        print("Fichier introuvable (aucun des chemins suivants n'existe) :")
        for c in candidates:
            print(" -", str(c))
        return

    df = pd.read_csv(path)
    print(f"Fichier chargé : {path} ({len(df)} lignes)")

    records = convert_dataframe_types(df)

    if dry_run:
        print(f"Mode dry-run activé : {len(records)} documents préparés (aucune insertion effectuée)")
        sample = records[:5]
        print("Exemples de documents convertis (5 premiers) :")
        print(json_util.dumps(sample, indent=2, default=str))
        return

    inserted = 0
    for i in range(0, len(records), batch_size):
        batch = records[i : i + batch_size]
        try:
            res = coll.insert_many(batch, ordered=False)
            inserted += len(res.inserted_ids)
            print(f"Inséré {len(res.inserted_ids)} documents (total {inserted})")
        except Exception as e:
            print(f"Erreur insertion batch (i={i}): {e}")

    print(f"Import terminé. Documents insérés ~ {inserted} (voir la collection {db}.{collection})")


def find(uri: str, db: str, collection: str, filter_json: Optional[str], limit: int = 20):
    coll = get_collection(uri, db, collection)
    if filter_json:
        try:
            filt = json_util.loads(filter_json)
        except Exception as e:
            print(f"Impossible de parser le filtre JSON : {e}")
            return
    else:
        filt = {}

    cursor = coll.find(filt).limit(limit)
    docs = list(cursor)
    print(json_util.dumps(docs, indent=2, default=str))


def find_one(uri: str, db: str, collection: str, id_or_filter: str):
    coll = get_collection(uri, db, collection)
    try:
        _id = ObjectId(id_or_filter)
        doc = coll.find_one({"_id": _id})
        print(json_util.dumps(doc, indent=2, default=str))
        return
    except Exception:
        pass

    try:
        filt = json_util.loads(id_or_filter)
        doc = coll.find_one(filt)
        print(json_util.dumps(doc, indent=2, default=str))
    except Exception as e:
        print(f"Erreur: {e}")


def insert_one(uri: str, db: str, collection: str, doc_json: str):
    coll = get_collection(uri, db, collection)
    try:
        doc = json_util.loads(doc_json)
    except Exception as e:
        print(f"Impossible de parser le document JSON : {e}")
        return

    if "Age" in doc:
        doc["Age"] = _safe_int(doc.get("Age"))
    if "Date of Admission" in doc:
        doc["Date of Admission"] = _to_datetime(doc.get("Date of Admission"))

    res = coll.insert_one(doc)
    print(f"Document inséré avec _id: {res.inserted_id}")


def update_one(uri: str, db: str, collection: str, filter_json: str, update_json: str, upsert: bool = False):
    coll = get_collection(uri, db, collection)
    try:
        filt = json_util.loads(filter_json)
        update_doc = json_util.loads(update_json)
    except Exception as e:
        print(f"Erreur parsing JSON : {e}")
        return

    if not any(k.startswith("$") for k in update_doc.keys()):
        update_doc = {"$set": update_doc}

    res = coll.update_one(filt, update_doc, upsert=upsert)
    print(f"Matched: {res.matched_count}, Modified: {res.modified_count}, UpsertedId: {res.upserted_id}")


def delete_one(uri: str, db: str, collection: str, filter_json: str):
    coll = get_collection(uri, db, collection)
    try:
        filt = json_util.loads(filter_json)
    except Exception as e:
        print(f"Erreur parsing filter JSON : {e}")
        return

    res = coll.delete_one(filt)
    print(f"Deleted count: {res.deleted_count}")


def create_indexes(uri: str, db: str, collection: str):
    coll = get_collection(uri, db, collection)

    print("Création des index recommandés pour les requêtes communes :")

    print("- idx_name : accélère les recherches par nom (ex. find({'Name': ...}))")
    coll.create_index([("Name", pymongo.ASCENDING)], name="idx_name")

    print("- idx_date_admission : utile pour les recherches/ranges et tri par date")
    coll.create_index([("Date of Admission", pymongo.ASCENDING)], name="idx_date_admission")

    print("- idx_medical_condition : filtre/agrégation par pathologie")
    coll.create_index([("Medical Condition", pymongo.ASCENDING)], name="idx_medical_condition")

    print("- idx_name_date : index composé pour aider la détection de doublons (Name + Date of Admission)")
    coll.create_index([("Name", pymongo.ASCENDING), ("Date of Admission", pymongo.ASCENDING)], name="idx_name_date")

    print("- text_idx_medical_condition : index texte pour recherche libre sur Medical Condition")
    try:
        coll.create_index([("Medical Condition", "text")], name="text_idx_medical_condition")
    except Exception as e:
        print(f"Création index texte échouée (déjà existant?) : {e}")

    print("Indexes créés/confirmés. Vous les verrez également dans MongoDB Compass.")


def show_indexes(uri: str, db: str, collection: str):
    coll = get_collection(uri, db, collection)
    indexes = list(coll.list_indexes())
    print(json_util.dumps(indexes, indent=2, default=str))
