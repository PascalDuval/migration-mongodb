from pymongo import MongoClient
import pandas as pd

# Connexion MongoDB
client = MongoClient('mongodb://localhost:27017')
db = client['FirstTry']
collection = db['medic2']

# Pipeline avec arrondi de l’âge moyen
pipeline = [
    {
        '$match': {
            'Age': { '$exists': True, '$ne': None, '$ne': '' }
        }
    },
    {
        '$project': {
            'Medical Condition': 1,
            'Age': { '$toInt': "$Age" }
        }
    },
    {
        '$group': {
            '_id': "$Medical Condition",
            'ageMoyen': { '$avg': "$Age" },
            'nbPatients': { '$sum': 1 }
        }
    },
    {
        '$project': {
            'ageMoyen': { '$round': ["$ageMoyen", 0] },  # ⬅️ arrondi entier
            'nbPatients': 1
        }
    },
    {
        '$sort': { 'ageMoyen': -1 }
    }
]

# Exécution
results = list(collection.aggregate(pipeline))

# Chargement pandas
df = pd.DataFrame(results)
df.rename(columns={
    '_id': 'Pathologie',
    'ageMoyen': 'Âge Moyen',
    'nbPatients': 'Nombre de Patients'
}, inplace=True)

# Conversion de l’âge moyen en entier (au cas où)
df['Âge Moyen'] = df['Âge Moyen'].astype(int)

# Affichage
print("\n📊 Âge moyen (arrondi) des patients selon les pathologies\n")
print(df.to_string(index=False))
