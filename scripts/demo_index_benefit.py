"""Demonstration: montrer l'utilité des index présents sur une collection.

Le script :
- liste les index
- construit des requêtes représentatives (find by Name, range sur Date of Admission,
  filter par Medical Condition, recherche texte) à partir d'un document échantillon
- exécute explain(mode='executionStats') pour chaque requête
- affiche un tableau simple comparant docsExamined / keysExamined / executionTimeMillis

Utilise `scripts.functions_crud.crud_ops.get_collection` pour se connecter.
"""
from __future__ import annotations

import argparse
import pprint
from typing import Dict, Any

# bson.json_util non nécessaire ici
from scripts.functions_crud.crud_ops import get_collection, DEFAULT_URI, DEFAULT_DB, DEFAULT_COLLECTION


def explain_for_query(coll, query: Dict[str, Any]):
    # explain via command to request executionStats
    return coll.database.command({'explain': {'find': coll.name, 'filter': query}, 'verbosity': 'executionStats'})


def summarize_explain(explain: Dict[str, Any]):
    stats = explain.get('executionStats', {})
    qp = explain.get('queryPlanner', {})
    winning = qp.get('winningPlan', {})
    return {
        'winning_stage': winning.get('stage'),
        'totalDocsExamined': stats.get('totalDocsExamined'),
        'totalKeysExamined': stats.get('totalKeysExamined'),
        'nReturned': stats.get('nReturned'),
        'executionTimeMillis': stats.get('executionTimeMillis')
    }


def main(uri: str, db_name: str, coll_name: str) -> int:
    coll = get_collection(uri, db_name, coll_name)

    print('\nIndexes présents:')
    for idx in coll.list_indexes():
        print(' -', idx['name'], 'keys=', idx['key'])

    sample = coll.find_one()
    if not sample:
        print('Collection vide — rien à démontrer')
        return 1

    # Construire des queries représentatives
    queries = []
    # 1) recherche par Name si présent
    if 'Name' in sample:
        queries.append(('find_by_name', {'Name': sample['Name']}))

    # 2) range sur Date of Admission (dernier an) si présent
    if 'Date of Admission' in sample:
        doa = sample['Date of Admission']
        # construire un range autour de la date sample
        try:
            start = doa
            end = doa
            queries.append(('range_date_admission', {'Date of Admission': {'$gte': start, '$lte': end}}))
        except Exception:
            pass

    # 3) filter par Medical Condition
    if 'Medical Condition' in sample:
        queries.append(('filter_medical_condition', {'Medical Condition': sample['Medical Condition']}))

    # 4) text search sur Medical Condition si index texte présent
    has_text = any('text' in list(idx['key'].values()) for idx in coll.list_indexes())
    if has_text and 'Medical Condition' in sample:
        queries.append(('text_search_medical', {'$text': {'$search': sample['Medical Condition']}}))

    results = {}
    for name, q in queries:
        print(f"\n--- Explain pour '{name}' --> query: {q}")
        try:
            ex = explain_for_query(coll, q)
            summ = summarize_explain(ex)
            results[name] = summ
            pprint.pprint(summ)
        except Exception as e:
            print('Erreur explain:', e)

    print('\nRésumé comparatif (docsExamined / keysExamined / time ms):')
    for k, v in results.items():
        print(f"{k}: docs={v.get('totalDocsExamined')} keys={v.get('totalKeysExamined')} time_ms={v.get('executionTimeMillis')}")

    return 0


def parse_args():
    p = argparse.ArgumentParser(description='Demo index benefit')
    p.add_argument('--uri', default=DEFAULT_URI)
    p.add_argument('--db', default=DEFAULT_DB)
    p.add_argument('--collection', default=DEFAULT_COLLECTION)
    return p.parse_args()


if __name__ == '__main__':
    args = parse_args()
    raise SystemExit(main(args.uri, args.db, args.collection))
