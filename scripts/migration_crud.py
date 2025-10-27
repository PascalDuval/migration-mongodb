#!/usr/bin/env python3
"""
migration_crud.py

Outil de migration pour MongoDB.

Fonctionnalités principales :
- import_csv : lire un CSV, convertir les types (Age -> int, Date of Admission -> datetime)
  puis insérer dans la collection (insert_many).
- find / find_one : requêtes de lecture avec filtres JSON.
- insert_one : insérer un document depuis une chaîne JSON.
- update_one : mise à jour (supporte `$set`) depuis filtres et document JSON.
- delete_one : suppression selon filtre JSON.

Usage (exemples) :
  python scripts/migration_crud.py import_csv --file ../data/healthcare_dataset_purge.csv
  python scripts/migration_crud.py find --filter '{"Name": "John Doe"}'

Par défaut : uri = 'mongodb://localhost:27017', db = 'FirstTry', collection = 'mediccrud'
"""

from __future__ import annotations
import argparse
from typing import Any, Dict, List, Optional
from pathlib import Path
from datetime import datetime
import pandas as pd
import pymongo
from pymongo import MongoClient
from bson import json_util, ObjectId


# === CONFIGURATION PAR DÉFAUT ===
DEFAULT_URI = "mongodb://localhost:27017"
DEFAULT_DB = "FirstTry"
DEFAULT_COLLECTION = "mediccrud"


# === CONNEXION MONGODB ===
def get_collection(uri: str, db_name: str, coll_name: str):
    client = MongoClient(uri)
    db = client[db_name]
    return db[coll_name]


# === CONVERSIONS DE TYPES ===
def _safe_int(value: Any) -> Optional[int]:
    try:
        if pd.isna(value):
            return None
        return int(float(value))
    except Exception:
        return None


def _to_datetime(value: Any) -> Optional[datetime]:
    """Convertit différentes représentations en datetime Python ou renvoie None."""
    if value is None:
        return None

    try:
        if isinstance(value, pd.Timestamp):
            return None if pd.isna(value) else value.to_pydatetime()
    except Exception:
        pass

    try:
        ts = pd.to_datetime(value, errors="coerce", dayfirst=False)
        return None if pd.isna(ts) else ts.to_pydatetime()
    except Exception:
        return None


def convert_dataframe_types(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Convertit les colonnes connues en types appropriés et retourne une liste de dicts."""
    df2 = df.copy()

    if "Age" in df2.columns:
        df2["Age"] = pd.to_numeric(df2["Age"], errors="coerce").astype(pd.Int64Dtype())

    if "Date of Admission" in df2.columns:
        df2["Date of Admission"] = pd.to_datetime(df2["Date of Admission"], errors="coerce")

    records: List[Dict[str, Any]] = []
    for _, row in df2.iterrows():
        doc: Dict[str, Any] = {}
        for k, v in row.items():
            if pd.isna(v):
                doc[k] = None
                continue
            if k == "Age":
                doc[k] = _safe_int(v)
            elif k == "Date of Admission":
                doc[k] = _to_datetime(v)
            else:
                doc[k] = v
        records.append(doc)
    return records


# === IMPORT CSV ===
def import_csv(uri: str, db: str, collection: str, file: str, batch_size: int = 1000, dry_run: bool = False):
    coll = get_collection(uri, db, collection)

    candidates = [
        Path(file),
        Path(__file__).parent.joinpath(file),
        Path.cwd().joinpath(file),
        Path.cwd().joinpath("data", Path(file).name),
        Path(__file__).parent.parent.joinpath("data", Path(file).name),
    ]

    path = next((c for c in candidates if c.exists()), None)
    if path is None:
        print("❌ Fichier introuvable (aucun des chemins suivants n'existe) :")
        for c in candidates:
            print(" -", str(c))
        return

    df = pd.read_csv(path)
    print(f"✅ Fichier chargé : {path} ({len(df)} lignes)")
    records = convert_dataframe_types(df)

    if dry_run:
        print(f"🔍 Mode dry-run : {len(records)} documents préparés (aucune insertion)")
        print("Exemples de documents convertis (5 premiers) :")
        print(json_util.dumps(records[:5], indent=2, default=str))
        return

    inserted = 0
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        try:
            res = coll.insert_many(batch, ordered=False)
            inserted += len(res.inserted_ids)
            print(f"📥 Insertion batch : {len(res.inserted_ids)} (total {inserted})")
        except Exception as e:
            print(f"⚠️ Erreur lors de l'insertion (batch {i}): {e}")

    print(f"🎯 Import terminé : {inserted} documents insérés dans {db}.{collection}")


# === OPÉRATIONS CRUD ===
def find(uri: str, db: str, collection: str, filter_json: Optional[str], limit: int = 20):
    coll = get_collection(uri, db, collection)
    filt = json_util.loads(filter_json) if filter_json else {}
    docs = list(coll.find(filt).limit(limit))
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
        print(f"⚠️ Erreur parsing JSON : {e}")


def insert_one(uri: str, db: str, collection: str, doc_json: str):
    coll = get_collection(uri, db, collection)
    doc = json_util.loads(doc_json)
    if "Age" in doc:
        doc["Age"] = _safe_int(doc.get("Age"))
    if "Date of Admission" in doc:
        doc["Date of Admission"] = _to_datetime(doc.get("Date of Admission"))
    res = coll.insert_one(doc)
    print(f"✅ Document inséré (_id={res.inserted_id})")


def update_one(uri: str, db: str, collection: str, filter_json: str, update_json: str, upsert: bool = False):
    coll = get_collection(uri, db, collection)
    filt = json_util.loads(filter_json)
    update_doc = json_util.loads(update_json)
    if not any(k.startswith("$") for k in update_doc.keys()):
        update_doc = {"$set": update_doc}
    res = coll.update_one(filt, update_doc, upsert=upsert)
    print(f"🔄 Matched: {res.matched_count}, Modified: {res.modified_count}, UpsertedId: {res.upserted_id}")


def delete_one(uri: str, db: str, collection: str, filter_json: str):
    coll = get_collection(uri, db, collection)
    filt = json_util.loads(filter_json)
    res = coll.delete_one(filt)
    print(f"🗑️ Documents supprimés : {res.deleted_count}")


# === ARGUMENTS CLI ===
def parse_args():
    parser = argparse.ArgumentParser(description="Migration CRUD simplifiée pour MongoDB")
    parser.add_argument("--uri", default=DEFAULT_URI, help="URI MongoDB (défaut localhost)")
    parser.add_argument("--db", default=DEFAULT_DB, help="Nom de la base (défaut FirstTry)")
    parser.add_argument("--collection", default=DEFAULT_COLLECTION, help="Nom de la collection (défaut mediccrud)")

    sub = parser.add_subparsers(dest="cmd")

    sp = sub.add_parser("import_csv")
    sp.add_argument("--file", default="../data/healthcare_dataset_purge.csv")
    sp.add_argument("--batch", type=int, default=1000)
    sp.add_argument("--dry", action="store_true")

    sp = sub.add_parser("find")
    sp.add_argument("--filter", default=None)
    sp.add_argument("--limit", type=int, default=20)

    sp = sub.add_parser("find_one")
    sp.add_argument("id_or_filter")

    sp = sub.add_parser("insert_one")
    sp.add_argument("doc_json")

    sp = sub.add_parser("update_one")
    sp.add_argument("filter_json")
    sp.add_argument("update_json")
    sp.add_argument("--upsert", action="store_true")

    sp = sub.add_parser("delete_one")
    sp.add_argument("filter_json")

    return parser.parse_args()


# === POINT D’ENTRÉE ===
def main():
    args = parse_args()
    if args.cmd == "import_csv":
        import_csv(args.uri, args.db, args.collection, args.file, batch_size=args.batch, dry_run=getattr(args, 'dry', False))
    elif args.cmd == "find":
        find(args.uri, args.db, args.collection, args.filter, limit=args.limit)
    elif args.cmd == "find_one":
        find_one(args.uri, args.db, args.collection, args.id_or_filter)
    elif args.cmd == "insert_one":
        insert_one(args.uri, args.db, args.collection, args.doc_json)
    elif args.cmd == "update_one":
        update_one(args.uri, args.db, args.collection, args.filter_json, args.update_json, upsert=args.upsert)
    elif args.cmd == "delete_one":
        delete_one(args.uri, args.db, args.collection, args.filter_json)
    else:
        print("❓ Aucune commande fournie. Utilisez --help pour voir les options.")


if __name__ == "__main__":
    main()
