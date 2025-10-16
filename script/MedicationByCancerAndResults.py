from pymongo import MongoClient

# Connexion MongoDB
client = MongoClient('mongodb://localhost:27017')
db = client['FirstTry']
collection = db['medic2']

# Pipeline d'agrégation
pipeline = [
    {
        '$match': {
            'Medical Condition': 'Cancer'  # sensible à la casse
        }
    },
    {
        '$group': {
            '_id': '$Medication',
            'testResults': {'$push': '$Test Results'}
        }
    },
    {
        '$project': {
            '_id': 1,
            'totalTests': {'$size': '$testResults'},
            'abnormalPercent': {
                '$multiply': [
                    {
                        '$divide': [
                            {
                                '$size': {
                                    '$filter': {
                                        'input': '$testResults',
                                        'as': 'result',
                                        'cond': {'$eq': ['$$result', 'Abnormal']}
                                    }
                                }
                            },
                            {'$size': '$testResults'}
                        ]
                    },
                    100
                ]
            },
            'inconclusivePercent': {
                '$multiply': [
                    {
                        '$divide': [
                            {
                                '$size': {
                                    '$filter': {
                                        'input': '$testResults',
                                        'as': 'result',
                                        'cond': {'$eq': ['$$result', 'Inconclusive']}
                                    }
                                }
                            },
                            {'$size': '$testResults'}
                        ]
                    },
                    100
                ]
            },
            'normalPercent': {
                '$multiply': [
                    {
                        '$divide': [
                            {
                                '$size': {
                                    '$filter': {
                                        'input': '$testResults',
                                        'as': 'result',
                                        'cond': {'$eq': ['$$result', 'Normal']}
                                    }
                                }
                            },
                            {'$size': '$testResults'}
                        ]
                    },
                    100
                ]
            }
        }
    }
]

# Exécution de l'agrégation
results = collection.aggregate(pipeline)

# Affichage formaté
print("\n📊 Analyse des résultats de tests pour la condition 'Cancer':\n")
print("{:<30}{:<15}{:<18}{:<20}{:<15}".format(
    "Médicament", "Tests", "% Anormal", "% Inconclusive", "% Normal"
))
print("-" * 100)

for doc in results:
    medication = doc['_id'] if doc['_id'] else "Inconnu"
    total = doc['totalTests']
    abnormal = round(doc['abnormalPercent'], 2)
    inconclusive = round(doc['inconclusivePercent'], 2)
    normal = round(doc['normalPercent'], 2)

    print("{:<30}{:<15}{:<18}{:<20}{:<15}".format(
        medication, total, f"{abnormal}%", f"{inconclusive}%", f"{normal}%"
    ))
