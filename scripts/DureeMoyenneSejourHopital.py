from pymongo import MongoClient

# Connexion MongoDB
client = MongoClient('mongodb://localhost:27017')
db = client['FirstTry']
collection = db['medic2']

# Pipeline d'agrégation pour la durée moyenne de séjour
pipeline = [
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
        '$group': {
            '_id': None,
            'averageStay': { '$avg': "$stayDuration" }
        }
    }
]

# Exécution
result = collection.aggregate(pipeline)

# Affichage
print("\n🏥 Durée moyenne de séjour à l’hôpital :\n")
for doc in result:
    print(f"📅 {round(doc['averageStay'], 2)} jours")
