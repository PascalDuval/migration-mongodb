import csv
from pymongo import MongoClient

# Connexion à la base MongoDB locale
client = MongoClient('mongodb://localhost:27017')
db = client['FirstTry']
collection = db['medic2']


# Chemin vers votre fichier CSV
csv_file_path = 'healthcare_dataset_purge.csv'
# csv_file_path = '../data/healthcare_dataset_purge.csv'



with open(csv_file_path, mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)  # Lecture en dict pour avoir les colonnes comme clés
    data = []
    for row in reader:
        # Ici, vous pouvez transformer les valeurs si besoin, par exemple convertir en int/float
        data.append(row)
    if data:
        collection.insert_many(data)

print("Import terminé avec succès.")

for doc in collection.find().limit(5):
    print(doc)
