from pymongo import MongoClient

# Connexion à MongoDB
client = MongoClient('mongodb://localhost:27017')

# Sélection de la base de données et de la collection
db = client['FirstTry']
collection = db['medic2']

# Pipeline d'agrégation
pipeline = [
    {
        '$match': {
            'Medical Condition': 'Cancer'
        }
    },
    {
        '$group': {
            '_id': '$Medication',
            'count': {'$sum': 1}
        }
    }
]

# Exécution de la requête d'agrégation
results = collection.aggregate(pipeline)

# Affichage formaté des résultats
print("\n📊 Médicaments associés à la condition 'Cancer':\n")
print("{:<30}{}".format("Médicament", "Nombre de cas"))
print("-" * 45)

for doc in results:
    medication = doc['_id'] if doc['_id'] else "Inconnu"
    count = doc['count']
    print("{:<30}{}".format(medication, count))
