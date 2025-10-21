from pymongo import MongoClient
import json


def short_type_name(value):
    if value is None:
        return 'None'
    return value.__class__.__name__


def extract_explain_summary(explain):
    qp = explain.get('queryPlanner', {})
    winning = qp.get('winningPlan', {})
    exec_stats = explain.get('executionStats', {})

    stage = winning.get('stage')
    plan_str = json.dumps(winning, default=str)
    ixscan = 'IXSCAN' in plan_str
    collscan = 'COLLSCAN' in plan_str

    summary = {
        'winning_stage': stage,
        'ixscan': ixscan,
        'collscan': collscan,
        'nReturned': exec_stats.get('nReturned'),
        'executionTimeMillis': exec_stats.get('executionTimeMillis'),
        'totalKeysExamined': exec_stats.get('totalKeysExamined'),
        'totalDocsExamined': exec_stats.get('totalDocsExamined')
    }
    return summary


def main():
    client = MongoClient('mongodb://localhost:27017')
    db = client.get_database('FirstTry')
    coll = db.get_collection('mediccrud')

    print('\n=== INDEXS sur FirstTry.mediccrud===\n')
    try:
        indexes = coll.index_information()
    except Exception as e:
        print(f'Erreur en récupérant les index: {e}')
        return 1

    if not indexes:
        print('Aucun index trouvé')
    else:
        for name, info in indexes.items():
            keys = info.get('key')
            unique = info.get('unique', False)
            partial = info.get('partialFilterExpression')
            print(f"- Index '{name}': keys={keys}, unique={unique}" + (f", partial={partial}" if partial else ""))

    sample = coll.find_one(projection={'Date of Admission': 1, 'Discharge Date': 1})
    print('\n=== ÉCHANTILLON : types des champs de date ===\n')
    if sample:
        doa = sample.get('Date of Admission')
        dd = sample.get('Discharge Date')
        print(f"Date of Admission: {short_type_name(doa)} -> {doa}")
        print(f"Discharge Date:    {short_type_name(dd)} -> {dd}")
    else:
        print('Aucun document trouvé dans la collection')

    # Expliquer uniquement le $match initial (sécurité si champs string)
    match_filter = {'Date of Admission': {'$exists': True, '$ne': None}, 'Discharge Date': {'$exists': True, '$ne': None}}
    print('\n=== explain() du $match initial (vérifier usage d\'index) ===\n')
    try:
        explain = db.command({'explain': {'find': 'medic2', 'filter': match_filter}})
    except Exception as e:
        print(f"Erreur lors de l'explain du $match: {e}")
        return 1

    summary = extract_explain_summary(explain)
    print(f"Plan gagnant (winning stage) : {summary.get('winning_stage')}")
    print(f"IXSCAN détecté : {summary.get('ixscan')}")
    print(f"COLLSCAN détecté : {summary.get('collscan')}")
    print(f"Docs examinés : {summary.get('totalDocsExamined')}")
    print(f"Keys examinés : {summary.get('totalKeysExamined')}")
    print(f"Résultats retournés : {summary.get('nReturned')}")
    print(f"Temps d'exécution (ms) : {summary.get('executionTimeMillis')}\n")

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
