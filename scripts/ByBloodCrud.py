from pymongo import MongoClient
from pymongo.errors import PyMongoError

def main():
    client = MongoClient('mongodb://localhost:27017')
    db = client.get_database('FirstTry')
    collection = db.get_collection('medic2')

    # Filtrer d'abord sur l'existence du champ pour profiter d'un index éventuel
    pipeline = [
        {
            '$match': {
                'Blood Type': { '$exists': True, '$ne': None }
            }
        },
        {
            '$group': {
                '_id': '$Blood Type',
                'count': { '$sum': 1 }
            }
        },
        {
            '$group': {
                '_id': None,
                'total': { '$sum': '$count' },
                'data': { '$push': { 'Blood Type': '$_id', 'count': '$count' } }
            }
        },
        { '$unwind': '$data' },
        {
            '$project': {
                '_id': 0,
                'Blood Type': '$data.Blood Type',
                'count': '$data.count',
                'percentage': { '$multiply': [ { '$divide': [ '$data.count', '$total' ] }, 100 ] }
            }
        },
        { '$sort': { 'count': -1 } }
    ]

    try:
        results = list(collection.aggregate(pipeline))
    except PyMongoError as e:
        print(f"Erreur MongoDB lors de l'agrégation : {e}")
        return 1

    # Essayer de formater avec pandas si disponible
    try:
        import pandas as pd
        df = pd.DataFrame(results)
        df.rename(columns={'count': 'Nombre de Patients', 'percentage': 'Pourcentage'}, inplace=True)
        df['Pourcentage'] = df['Pourcentage'].map("{:.2f}%".format)
        print("\n🧬 Histogramme des Groupes Sanguins (CRUD) :\n")
        print(df.to_string(index=False))
    except Exception:
        # Fallback simple
        print("\n🧬 Histogramme des Groupes Sanguins (CRUD) — fallback :\n")
        for doc in results:
            bt = doc.get('Blood Type')
            cnt = doc.get('count')
            pct = doc.get('percentage')
            print(f"{bt}: {cnt} ({pct:.2f}%)")

    return 0

if __name__ == '__main__':
    raise SystemExit(main())
