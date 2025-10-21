import json
from pymongo import MongoClient

def main():
    client = MongoClient('mongodb://localhost:27017')
    db = client.get_database('FirstTry')
    coll_name = 'medic2'

    pipeline = [
        {
            '$match': {
                'Date of Admission': { '$exists': True, '$ne': None, '$type': 'string' },
                'Discharge Date': { '$exists': True, '$ne': None, '$type': 'string' }
            }
        },
        {
            '$project': {
                'stayDuration': {
                    '$dateDiff': {
                        'startDate': { '$toDate': "$Date of Admission" },
                        'endDate': { '$toDate': "$Discharge Date" },
                        'unit': "day"
                    }
                }
            }
        },
        {
            '$match': { 'stayDuration': { '$gte': 0 } }
        },
        {
            '$group': {
                '_id': None,
                'averageStay': { '$avg': "$stayDuration" },
                'count': { '$sum': 1 }
            }
        }
    ]

    # Use the explain command for aggregation
    try:
        explain = db.command({ 'explain': { 'aggregate': coll_name, 'pipeline': pipeline, 'cursor': {} } })
    except Exception as e:
        print(f"Erreur lors de l'explain: {e}")
        return 1

    # Print a compact summary: look for IXSCAN vs COLLSCAN in the plan
    explain_str = json.dumps(explain, default=str)
    ix_used = 'IXSCAN' in explain_str
    collscan_used = 'COLLSCAN' in explain_str

    print("--- Résumé explain() ---")
    print(f"Index scan détecté (IXSCAN) : {ix_used}")
    print(f"Scan collection détecté (COLLSCAN) : {collscan_used}")
    print('\n--- explain complet (truncated) ---')
    # print first 2000 chars to avoid flooding
    print(explain_str[:2000])

    return 0

if __name__ == '__main__':
    raise SystemExit(main())
