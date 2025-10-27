#!/usr/bin/env python3
"""
migration_crud.py
Version corrigée pour compatibilité Docker / argparse (2025)
"""

from __future__ import annotations
import argparse
from typing import Any, Dict, List, Optional
from pathlib import Path
import pandas as pd
from pymongo import MongoClient
from bson import json_util, ObjectId
from datetime import datetime

DEFAULT_URI = "mongodb://localhost:27017"
DEFAULT_DB = "FirstTry"
DEFAULT_COLLECTION = "mediccrud"


# === Connexion MongoDB ===
def get_collection(uri: str, db_name: str, coll_name: str):
    client = MongoClient(uri)
    db = client[db_name]
    return db[coll_name]


# === Helpers ===
def _safe_int(value: Any) -> Optional[int]:
    try:
        if pd.isna(value):
            return None
        return int(float(value))
    except Exception:
        return None


def _to_datetime(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    try:
        ts = pd.to_datetime(value, errors="coerce", dayfirst=False)
        if pd.isna(ts):
            return None
        return ts.to_pydatetime()
    except Exception:
        return None


# === CSV import ===
def convert_dataframe_types(df: pd.DataFrame) -> List[Dict[str, Any]]:
    df2 = df.copy()
    if "Age" in df2.columns:
        df2["Age"] = pd.to_numeric(df2["Age"], errors="coerce").astype(pd.Int64Dtype())
    if "Date of Admission" in df2.columns:
        df2["Date of Admission"] = pd.to_datetime(df2["Date of Admission"], errors="coerce")

    records = []
    for _, row in df2.iterrows():
        doc = {}
        for k, v in row.items():
            if pd.isna(v):
                doc[k] = None
            elif k == "Age":
                doc[k] = _safe_int(v)
            elif k == "Date of Admission":
                doc[k] = _to_datetime(v)
            else:
                doc[k] = v
        records.append(doc)
    return records


def import_csv(uri: str, db: str, collection: str, file: str, batch_size: int = 1000, dry_run: bool = False):
    coll = get_collection(uri, db, collection)

    candidates = [
        Path(file),
        Path.cwd().joinpath(file),
        Path.cwd().joinpath("data", Path(file).name),
    ]
    path = next((c for c in candidates if c.exists()), None)
    if path is None:
        print("❌ Fichier introuvable.")
        return

    df = pd.read_csv(path)
    print(f"📄 Fichier chargé : {path} ({len(df)} lignes)")
    records = convert_dataframe_types(df)

    if dry_run:
        print(f"Mode dry-run activé ({len(records)} documents)")
        return

    inserted = 0
    for i in range(0, len(records), batch_size):
        batch = records[i:i+batch_size]
        res = coll.insert_many(batch, ordered=False)
        inserted += len(res.inserted_ids)
        print(f"✅ Batch {i//batch_size+1}: {len(res.inserted_ids)} insérés (total {inserted})")

    print(f"🎯 Import terminé. {inserted} documents insérés dans {db}.{collection}")


# === CRUD ===
def find(uri, db, collection, filter_json, limit):
    coll = get_collection(uri, db, collection)
    filt = json_util.loads(filter_json) if filter_json else {}
    docs = list(coll.find(filt).limit(limit))
    print(json_util.dumps(docs, indent=2, default=str))


def find_one(uri, db, collection, id_or_filter):
    coll = get_collection(uri, db, collection)
    try:
        filt = {"_id": ObjectId(id_or_filter)}
    except Exception:
        filt = json_util.loads(id_or_filter)
    doc = coll.find_one(filt)
    print(json_util.dumps(doc, indent=2, default=str))


def insert_one(uri, db, collection, doc_json):
    coll = get_collection(uri, db, collection)
    doc = json_util.loads(doc_json)
    res = coll.insert_one(doc)
    print(f"✅ Document inséré : {res.inserted_id}")


def update_one(uri, db, collection, filter_json, update_json, upsert=False):
    coll = get_collection(uri, db, collection)
    filt = json_util.loads(filter_json)
    update = json_util.loads(update_json)
    if not any(k.startswith("$") for k in update):
        update = {"$set": update}
    res = coll.update_one(filt, update, upsert=upsert)
    print(f"Matched: {res.matched_count}, Modified: {res.modified_count}")


def delete_one(uri, db, collection, filter_json):
    coll = get_collection(uri, db, collection)
    filt = json_util.loads(filter_json)
    res = coll.delete_one(filt)
    print(f"🗑️ Supprimés : {res.deleted_count}")


# === Argparse corrigé ===
def parse_args():
    parser = argparse.ArgumentParser(description="Migration CRUD pour MongoDB")

    # arguments communs
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--uri", default=DEFAULT_URI)
    common.add_argument("--db", default=DEFAULT_DB)
    common.add_argument("--collection", default=DEFAULT_COLLECTION)

    sub = parser.add_subparsers(dest="cmd")

    sp = sub.add_parser("import_csv", parents=[common])
    sp.add_argument("--file", default="data/healthcare_dataset_purge.csv")
    sp.add_argument("--batch", type=int, default=1000)
    sp.add_argument("--dry", action="store_true")

    sp = sub.add_parser("find", parents=[common])
    sp.add_argument("--filter", default=None)
    sp.add_argument("--limit", type=int, default=20)

    sp = sub.add_parser("find_one", parents=[common])
    sp.add_argument("id_or_filter")

    sp = sub.add_parser("insert_one", parents=[common])
    sp.add_argument("doc_json")

    sp = sub.add_parser("update_one", parents=[common])
    sp.add_argument("filter_json")
    sp.add_argument("update_json")
    sp.add_argument("--upsert", action="store_true")

    sp = sub.add_parser("delete_one", parents=[common])
    sp.add_argument("filter_json")

    return parser.parse_args()


def main():
    args = parse_args()

    if args.cmd == "import_csv":
        import_csv(args.uri, args.db, args.collection, args.file, args.batch, args.dry)
    elif args.cmd == "find":
        find(args.uri, args.db, args.collection, args.filter, args.limit)
    elif args.cmd == "find_one":
        find_one(args.uri, args.db, args.collection, args.id_or_filter)
    elif args.cmd == "insert_one":
        insert_one(args.uri, args.db, args.collection, args.doc_json)
    elif args.cmd == "update_one":
        update_one(args.uri, args.db, args.collection, args.filter_json, args.update_json, args.upsert)
    elif args.cmd == "delete_one":
        delete_one(args.uri, args.db, args.collection, args.filter_json)
    else:
        print("⚠️ Aucune commande fournie. Utilisez --help pour voir les options disponibles.")


if __name__ == "__main__":
    main()
