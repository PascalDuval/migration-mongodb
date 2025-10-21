#!/usr/bin/env python3
"""
backup_and_drop.py

Sauvegarde une collection MongoDB en JSONL dans le dossier `data/` puis supprime
la collection. Utilisé par le script PowerShell d'automatisation.

Usage:
  python scripts/backup_and_drop.py --uri mongodb://localhost:27017 --db FirstTry --collection mediccrud

Sortie:
  data/backup_mediccrud_YYYYmmdd_HHMMSS.jsonl
"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from bson import json_util
from pymongo import MongoClient


def parse_args():
    p = argparse.ArgumentParser(description="Backup puis drop d'une collection MongoDB")
    p.add_argument("--uri", default="mongodb://localhost:27017")
    p.add_argument("--db", default="FirstTry")
    p.add_argument("--collection", default="mediccrud")
    p.add_argument("--outdir", default="data")
    return p.parse_args()


def main():
    args = parse_args()
    client = MongoClient(args.uri)
    db = client[args.db]
    coll = db[args.collection]

    count = coll.count_documents({})
    print(f"Collection {args.db}.{args.collection} contient {count} documents")

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_file = outdir.joinpath(f"backup_{args.collection}_{ts}.jsonl")

    print(f"Sauvegarde dans {out_file} ...")
    with out_file.open("w", encoding="utf-8") as fh:
        cursor = coll.find({})
        for doc in cursor:
            fh.write(json_util.dumps(doc))
            fh.write("\n")

    print(f"Sauvegarde terminée : {out_file}")
    print(f"Suppression de la collection {args.db}.{args.collection} ...")
    coll.drop()
    print("Suppression terminée.")


if __name__ == '__main__':
    main()
