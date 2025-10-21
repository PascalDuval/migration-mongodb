from pymongo import MongoClient
from pymongo.errors import PyMongoError

def main():
    # Connexion MongoDB (utilise l'instance locale par défaut)
    client = MongoClient('mongodb://localhost:27017')
    db = client.get_database('FirstTry')
    collection = db.get_collection('medic2')

    # Détecter le type des champs dans la collection (échantillon) pour choisir
    sample = collection.find_one(projection={'Date of Admission': 1, 'Discharge Date': 1})
    use_date_type = False
    if sample:
        doa = sample.get('Date of Admission')
        dd = sample.get('Discharge Date')
        # Si les valeurs sont déjà de type datetime.datetime dans Python, alors c'est du type Date dans MongoDB
        import datetime
        if isinstance(doa, datetime.datetime) and isinstance(dd, datetime.datetime):
            use_date_type = True

    if use_date_type:
        # Si les champs sont stockés en type Date, on peut faire un $match direct (utilise l'index)
        pipeline = [
            {
                '$match': {
                    'Date of Admission': { '$exists': True, '$ne': None },
                    'Discharge Date': { '$exists': True, '$ne': None }
                }
            },
            {
                '$project': {
                    'stayDuration': {
                        '$dateDiff': {
                            'startDate': "$Date of Admission",
                            'endDate': "$Discharge Date",
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
    else:
        # Cas existant : champs en string -> conversion
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

    try:
        result = list(collection.aggregate(pipeline))
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

if __name__ == '__main__':
    raise SystemExit(main())
