from pymongo import MongoClient

# Connexion MongoDB
client = MongoClient('mongodb://localhost:27017')
db = client['FirstTry']
collection = db['medic2']

# Pipeline : Grouper par hôpital et compter les admissions
pipeline = [
    {
        '$group': {
            '_id': "$Hospital",
            'admissionCount': { '$sum': 1 }
        }
    },
    {
        '$sort': { 'admissionCount': -1 }
    },
    {
        '$limit': 1
    }
]

# Exécution
result = list(collection.aggregate(pipeline))

# Affichage du résultat
if result:
    top_hospital = result[0]['_id']
    count = result[0]['admissionCount']
    print(f"\n🏥 Hôpital avec le plus d'admissions : {top_hospital} ({count} admissions)")
else:
    print("❗ Aucun hôpital trouvé dans la base de données.")
