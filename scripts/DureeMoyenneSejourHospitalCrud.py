# typing.Optional not required
import argparse
import datetime

from pymongo.errors import PyMongoError

from scripts.functions_crud.crud_ops import get_collection, DEFAULT_URI, DEFAULT_DB


def build_pipeline(use_date_type: bool):
    if use_date_type:
        return [
            {
                '$match': {
                    'Date of Admission': {'$exists': True, '$ne': None},
                    'Discharge Date': {'$exists': True, '$ne': None}
                }
            },
            {
                '$project': {
                    'stayDuration': {
                        '$dateDiff': {
                            'startDate': '$Date of Admission',
                            'endDate': '$Discharge Date',
                            'unit': 'day'
                        }
                    }
                }
            },
            {'$match': {'stayDuration': {'$gte': 0}}},
            {'$group': {'_id': None, 'averageStay': {'$avg': '$stayDuration'}, 'count': {'$sum': 1}}}
        ]

    # string dates -> convert with $toDate
    return [
        {
            '$match': {
                'Date of Admission': {'$exists': True, '$ne': None, '$type': 'string'},
                'Discharge Date': {'$exists': True, '$ne': None, '$type': 'string'}
            }
        },
        {
            '$project': {
                'stayDuration': {
                    '$dateDiff': {
                        'startDate': {'$toDate': '$Date of Admission'},
                        'endDate': {'$toDate': '$Discharge Date'},
                        'unit': 'day'
                    }
                }
            }
        },
        {'$match': {'stayDuration': {'$gte': 0}}},
        {'$group': {'_id': None, 'averageStay': {'$avg': '$stayDuration'}, 'count': {'$sum': 1}}}
    ]


def main(uri: str, db_name: str, coll_name: str) -> int:
    coll = get_collection(uri, db_name, coll_name)

    sample = coll.find_one(projection={'Date of Admission': 1, 'Discharge Date': 1})
    use_date_type = False
    if sample:
        doa = sample.get('Date of Admission')
        dd = sample.get('Discharge Date')
        if isinstance(doa, datetime.datetime) and isinstance(dd, datetime.datetime):
            use_date_type = True

    pipeline = build_pipeline(use_date_type)

    try:
        result = list(coll.aggregate(pipeline))
    except PyMongoError as e:
        print(f"Erreur MongoDB lors de l'agrégation : {e}")
        return 1

    if not result:
        print("Aucun document correspondant (dates manquantes ou format non convertible).")
        return 0

    doc = result[0]
    average = doc.get('averageStay')
    count = doc.get('count', 0)

    if average is None:
        print("Impossible de calculer la durée moyenne — valeurs manquantes.")
        return 0

    print("\n🏥 Durée moyenne de séjour à l’hôpital (CRUD/filtrée) :\n")
    print(f"Nombre de séjours analysés : {count}")
    print(f"Durée moyenne : {round(average, 2)} jours")

    return 0


def parse_args():
    p = argparse.ArgumentParser(description="Calcul durée moyenne de séjour (utilise functions_crud.get_collection)")
    p.add_argument('--uri', default=DEFAULT_URI, help='URI MongoDB')
    p.add_argument('--db', default=DEFAULT_DB, help='Nom de la base')
    p.add_argument('--collection', default='medic2', help='Nom de la collection (défaut: medic2)')
    return p.parse_args()


if __name__ == '__main__':
    args = parse_args()
    raise SystemExit(main(args.uri, args.db, args.collection))
