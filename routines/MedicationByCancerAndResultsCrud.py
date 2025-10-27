#!/usr/bin/env python3

from pymongo import MongoClient
from collections import defaultdict, Counter
 

URI = 'mongodb://localhost:27017'
DB = 'FirstTry'
COL = 'mediccrud'

client = MongoClient(URI)
db = client[DB]
coll = db[COL]

# Filtre : Medical Condition contient 'Cancer' (insensible à la casse)
filter_q = {'Medical Condition': {'$regex': 'Cancer', '$options': 'i'}}

# Champs d'intérêt : Medication et Test Results
projection = {'Medication': 1, 'Test Results': 1}

cursor = coll.find(filter_q, projection)

# Regrouper par médicament
stats = defaultdict(lambda: Counter())

for doc in cursor:
    med = doc.get('Medication') or 'Inconnu'
    # Test Results peut être une valeur unique ou une liste ; on normalise
    tr = doc.get('Test Results')
    if tr is None:
        continue
    # Si c'est une liste, étendre
    if isinstance(tr, list):
        results = tr
    else:
        results = [tr]

    for r in results:
        key = str(r).strip()
        stats[med][key] += 1
        stats[med]['_total'] += 1

# Préparer les lignes et trier par nombre de tests décroissant
rows = []
for med, counter in stats.items():
    total = counter.get('_total', 0)
    if total == 0:
        continue
    abnormal = counter.get('Abnormal', 0)
    inconclusive = counter.get('Inconclusive', 0)
    normal = counter.get('Normal', 0)

    abnormal_pct = round((abnormal / total) * 100, 2) if total else 0.0
    inconclusive_pct = round((inconclusive / total) * 100, 2) if total else 0.0
    normal_pct = round((normal / total) * 100, 2) if total else 0.0

    rows.append((med, total, abnormal_pct, inconclusive_pct, normal_pct))

rows.sort(key=lambda x: x[1], reverse=True)  # tri par total décroissant

# Calcul des largeurs de colonne
hdr = ("Médicament", "Tests", "% Anormal", "% Inconclusive", "% Normal")
col_widths = [max(len(str(r[i])) for r in rows) if rows else len(hdr[i]) for i in range(5)]
for i, h in enumerate(hdr):
    col_widths[i] = max(col_widths[i], len(h))

sep = " | "

print("\n📊 Analyse (CRUD) des résultats de tests pour le diagnostic 'Cancer':\n")
# Header aligné
header_line = sep.join(h.ljust(col_widths[i]) for i, h in enumerate(hdr))
print(header_line)
print("-" * len(header_line))

for med, total, abnormal_pct, inconclusive_pct, normal_pct in rows:
    line = sep.join([
        str(med).ljust(col_widths[0]),
        str(total).rjust(col_widths[1]),
        (f"{abnormal_pct}%").rjust(col_widths[2]),
        (f"{inconclusive_pct}%").rjust(col_widths[3]),
        (f"{normal_pct}%").rjust(col_widths[4]),
    ])
    print(line)

