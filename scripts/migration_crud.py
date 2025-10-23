#!/usr/bin/env python3
"""
migration_crud.py


Fonctionnalités principales :
- import_csv : lire un CSV, convertir les types (Age -> int, Date of Admission -> datetime)
  puis insérer dans la collection (insert_many).
- find / find_one : requêtes de lecture avec filtres JSON
- insert_one : insérer un document depuis une chaîne JSON
- update_one : mise à jour (supporte `$set`) depuis filtres et document JSON
- delete_one : suppression selon filtre JSON
- create_indexes : crée des index recommandés et affiche pourquoi

Usage (exemples) :
  python scripts/migration_crud.py import_csv --file ../data/healthcare_dataset_purge.csv
  python scripts/migration_crud.py find --filter '{"Name": "John Doe"}'
  python scripts/migration_crud.py create_indexes

Par défaut : uri = 'mongodb://localhost:27017', db = 'FirstTry', collection = 'mediccrud'
"""

from __future__ import annotations

import argparse
from typing import Any, Dict, List, Optional
from pathlib import Path
 

import pandas as pd
import pymongo
from pymongo import MongoClient
from bson import json_util, ObjectId
from datetime import datetime


DEFAULT_URI = "mongodb://localhost:27017"
DEFAULT_DB = "FirstTry"
DEFAULT_COLLECTION = "mediccrud"


def get_collection(uri: str, db_name: str, coll_name: str):
    client = MongoClient(uri)
    db = client[db_name]
    return db[coll_name]


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
    # Si c'est déjà un pandas.Timestamp
    try:
        import pandas as _pd

        if isinstance(value, _pd.Timestamp):
            if pd.isna(value):
                return None
            return value.to_pydatetime()
    except Exception:
        pass

    # Essayer la conversion via pandas (tolérante)
    try:
        ts = pd.to_datetime(value, errors="coerce", dayfirst=False)
        if pd.isna(ts):
            return None
        return ts.to_pydatetime()
    except Exception:
        return None


def convert_dataframe_types(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Convertit les colonnes connues en types appropriés et retourne une liste de dicts.

    - 'Age' -> int (si possible)
    - 'Date of Admission' -> datetime
    """
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
                dt = _to_datetime(v)
                doc[k] = dt
            else:
                # garder le type tel quel (string, nombre, ...)
                doc[k] = v

        records.append(doc)
    return records


def import_csv(uri: str, db: str, collection: str, file: str, batch_size: int = 1000, dry_run: bool = False):
    coll = get_collection(uri, db, collection)

    # Chercher le fichier dans plusieurs emplacements plausibles pour être résilient
    candidates = [Path(file),
                  Path(__file__).parent.joinpath(file),
                  Path.cwd().joinpath(file),
                  Path.cwd().joinpath("data", Path(file).name),
                  Path(__file__).parent.parent.joinpath("data", Path(file).name)]

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

    # Si dry-run : afficher un résumé et quelques documents convertis sans écrire
    if dry_run:
        print(f"Mode dry-run activé : {len(records)} documents préparés (aucune insertion effectuée)")
        sample = records[:5]
        print("Exemples de documents convertis (5 premiers) :")
        print(json_util.dumps(sample, indent=2, default=str))
        return

    # Insérer par lots pour éviter de surcharger la mémoire
    inserted = 0
    for i in range(0, len(records), batch_size):
        batch = records[i : i + batch_size]
        # Convertir objets datetime en type acceptés par pymongo (datetime est OK)
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
    # essayer d'interpréter comme ObjectId
    try:
        _id = ObjectId(id_or_filter)
        doc = coll.find_one({"_id": _id})
        print(json_util.dumps(doc, indent=2, default=str))
        return
    except Exception:
        pass

    # sinon parser JSON comme filtre
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

    # conversion basique des types connus
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

    # si update_doc ne contient pas d'opérateur Mongo ($set, $inc...), on enveloppe avec $set
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
    """Crée des index utiles et affiche la raison pour chacun.

    Recommandations d'index proposées :
    - index sur `Name` (recherche rapide par nom)
    - index sur `Date of Admission` (requêtes temporelles / tris)
    - index sur `Medical Condition` (regroupements/filtrage)
    - index composé `Name + Date of Admission` (utile pour détection/fusion de doublons)
    - index texte sur `Medical Condition` pour recherche textuelle
    """
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


def parse_args():
    parser = argparse.ArgumentParser(description="Migration CRUD helper pour MongoDB")
    parser.add_argument("--uri", default=DEFAULT_URI, help="URI MongoDB (défaut localhost)")
    parser.add_argument("--db", default=DEFAULT_DB, help="Nom de la base (défaut FirstTry)")
    parser.add_argument("--collection", default=DEFAULT_COLLECTION, help="Nom de la collection (défaut mediccrud)")

    sub = parser.add_subparsers(dest="cmd")

    sp = sub.add_parser("import_csv")
    sp.add_argument("--file", default="../data/healthcare_dataset_purge.csv", help="Chemin vers le CSV à importer (défaut: ../data/healthcare_dataset_purge.csv)")
    sp.add_argument("--batch", type=int, default=1000, help="Taille des batches pour insert_many")
    sp.add_argument("--dry", action="store_true", help="Mode dry-run : convertir et compter les documents sans écrire en base")

    sp = sub.add_parser("find")
    sp.add_argument("--filter", default=None, help='Filtre JSON pour find (ex: "{"Name": "John"}")')
    sp.add_argument("--limit", type=int, default=20)

    sp = sub.add_parser("find_one")
    sp.add_argument("id_or_filter", help="_id (hex) ou filtre JSON")

    sp = sub.add_parser("insert_one")
    sp.add_argument("doc_json", help="Document JSON à insérer")

    sp = sub.add_parser("update_one")
    sp.add_argument("filter_json", help="Filtre JSON pour sélectionner le document à mettre à jour")
    sp.add_argument("update_json", help="Document d'update JSON (ou champs à $set)")
    sp.add_argument("--upsert", action="store_true")

    sp = sub.add_parser("delete_one")
    sp.add_argument("filter_json", help="Filtre JSON pour supprimer")

    sp = sub.add_parser("create_indexes")

    sp = sub.add_parser("show_indexes")

    return parser.parse_args()


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
    elif args.cmd == "create_indexes":
        create_indexes(args.uri, args.db, args.collection)
    elif args.cmd == "show_indexes":
        show_indexes(args.uri, args.db, args.collection)
    else:
        print("Aucune commande fournie. Utilisez --help pour voir les options.")


if __name__ == "__main__":
    main()
