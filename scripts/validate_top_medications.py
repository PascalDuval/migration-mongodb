#!/usr/bin/env python3
"""
validate_top_medications.py

Agrégation MongoDB pour lister les médicaments les plus prescrits aux patients
ayant une pathologie contenant 'Cancer'.

Usage:
  python scripts/validate_top_medications.py --top 10

"""
import argparse
from pymongo import MongoClient
from bson import json_util

URI = 'mongodb://localhost:27017'
DB = 'FirstTry'
COL = 'mediccrud'


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--top', type=int, default=10, help='Nombre de top médicaments à afficher')
    return p.parse_args()


def main():
    args = parse_args()
    client = MongoClient(URI)
    coll = client[DB][COL]

    pipeline = [
        {'$match': {'Medical Condition': {'$regex': 'Cancer', '$options': 'i'}}},
        {'$group': {'_id': '$Medication', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}},
        {'$limit': args.top}
    ]

    results = list(coll.aggregate(pipeline))
    print(json_util.dumps(results, indent=2, default=str))


if __name__ == '__main__':
    main()
