from pymongo import MongoClient
import pandas as pd

# Connexion MongoDB
client = MongoClient('mongodb://localhost:27017')
db = client['FirstTry']
collection = db['medic2']

# Pipeline pour histogramme + pourcentages (fourni par toi)
pipeline = [
    {
        '$group': {
            '_id': '$Blood Type',
            'count': {
                '$sum': 1
            }
        }
    },
    {
        '$group': {
            '_id': None,
            'total': {
                '$sum': '$count'
            },
            'data': {
                '$push': {
                    'Blood Type': '$_id',
                    'count': '$count'
                }
            }
        }
    },
    {
        '$unwind': '$data'
    },
    {
        '$project': {
            '_id': 0,
            'Blood Type': '$data.Blood Type',
            'count': '$data.count',
            'percentage': {
                '$multiply': [
                    {
                        '$divide': [
                            '$data.count', '$total'
                        ]
                    },
                    100
                ]
            }
        }
    }
]

# Exécution
results = list(collection.aggregate(pipeline))

# Création d'un DataFrame pandas
df = pd.DataFrame(results)

# Formatage
df.rename(columns={'count': 'Nombre de Patients', 'percentage': 'Pourcentage'}, inplace=True)
df['Pourcentage'] = df['Pourcentage'].map("{:.2f}%".format)

# Tri optionnel (du plus fréquent au moins)
df = df.sort_values(by='Nombre de Patients', ascending=False)

# Affichage final
print("\n🧬 Histogramme des Groupes Sanguins (calcul via MongoDB + sortie via pandas)\n")
print(df.to_string(index=False))
