from pymongo import MongoClient

# Connexion MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["FirstTry"]
collection = db["medic2"]

# ----------- CREATE -----------
print("\n📌 CREATE - Insertion d'un document")
new_patient = {
    "Name": "John Doe",
    "Age": "45",
    "Gender": "Male",
    "Medical Condition": "Asthma",
    "Blood Type": "O+",
    "Doctor": "Dr. Watson",
    "Date of Admission": "2023-01-10",
    "Discharge Date": "2023-01-15",
    "Medication": "Ventolin",
    "Test Results": "Normal",
    "Hospital": "LLC Smith",
    "Room Number": "B12",
    "Admission Type": "Urgence",
    "Billing Amount": "1500",
    "Insurance Provider": "ACME Health"
}
insert_result = collection.insert_one(new_patient)
print(f"✅ Document inséré avec _id : {insert_result.inserted_id}")

# ----------- READ -----------
print("\n📌 READ - Rechercher tous les patients ayant 'Asthma'")
asthma_patients = collection.find({"Medical Condition": "Asthma"})
for patient in asthma_patients:
    print(f"- {patient['Name']} ({patient['Age']} ans)")

# ----------- UPDATE -----------
print("\n📌 UPDATE - Mettre à jour le médecin de 'John Doe'")
update_result = collection.update_one(
    {"Name": "John Doe"},
    {"$set": {"Doctor": "Dr. House"}}
)
print(f"✅ {update_result.modified_count} document modifié.")

# ----------- DELETE -----------
print("\n📌 DELETE - Supprimer le patient 'John Doe'")
delete_result = collection.delete_one({"Name": "John Doe"})
print(f"🗑️ {delete_result.deleted_count} document supprimé.")
