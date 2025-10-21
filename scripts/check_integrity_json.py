"""
Script : check_integrity_json.py
But : Vérifier l'intégrité d'un fichier JSON MongoDB avant migration
Auteur : GPT-5 (Assistant Python)

Définition d’un doublon :
    - Même Name (insensible à la casse)
    - Age à ±7 ans
    - Même Gender, Blood Type, Doctor, Hospital, Billing Amount, Date of Admission
"""

import pandas as pd
import numpy as np
import os
import sys

# === CONFIGURATION ===
FICHIER_JSON = "../data/FirstTry.medic2.json"  # Fichier JSON MongoDB


# === 1. Chargement du fichier JSON ===
def charger_json(fichier):
    """Charge un fichier JSON (MongoDB export) et retourne un DataFrame pandas."""
    if not os.path.exists(fichier):
        print(f"❌ Erreur : Le fichier '{fichier}' est introuvable.")
        sys.exit(1)

    try:
        df = pd.read_json(fichier, lines=True)
    except ValueError:
        try:
            df = pd.read_json(fichier)
        except Exception as e:
            print(f"❌ Erreur lors du chargement du JSON : {e}")
            sys.exit(1)
    return df


# === 2. Vérification des colonnes ===
def verifier_colonnes(df):
    """Affiche la liste des colonnes et leur type."""
    print("\n📊 Colonnes disponibles et types de données :")
    print(df.dtypes)
    print(f"\nNombre total de colonnes : {len(df.columns)}")


# === 3. Vérification des valeurs manquantes ===
def verifier_valeurs_manquantes(df):
    """Vérifie la présence de valeurs manquantes."""
    print("\n🔍 Vérification des valeurs manquantes :")
    missing = df.isnull().sum()
    total_missing = missing.sum()

    if total_missing == 0:
        print("✅ Aucune valeur manquante détectée.")
    else:
        print(f"⚠️ Valeurs manquantes détectées dans {sum(missing > 0)} colonnes :")
        print(missing[missing > 0])


# === 4. Vérification des types mixtes ===
def verifier_types_mixtes(df):
    """Détecte les colonnes contenant des types de données mixtes."""
    print("\n🧩 Vérification des colonnes à types mixtes :")
    mixed_cols = []
    for col in df.columns:
        types_uniques = df[col].map(type).nunique()
        if types_uniques > 1:
            mixed_cols.append(col)

    if mixed_cols:
        print(f"⚠️ Colonnes avec types mixtes : {mixed_cols}")
        print("   → Recommandation : uniformiser les types (ex: int → str)")
    else:
        print("✅ Aucune colonne à types mixtes détectée.")


# === 5. Détection avancée de doublons ===
def verifier_doublons_personnalises(df):
    """
    Vérifie les doublons selon les critères personnalisés :
    - Name (insensible à la casse)
    - Age à ±7 ans
    - Gender, Blood Type, Doctor, Hospital, Billing Amount, Date of Admission
    """
    print("\n🧬 Vérification des doublons personnalisés :")

    # Colonnes requises
    required_cols = [
        "Name", "Age", "Gender", "Blood Type",
        "Doctor", "Hospital", "Billing Amount", "Date of Admission"
    ]

    for col in required_cols:
        if col not in df.columns:
            print(f"⚠️ Colonne manquante : {col}. Impossible de détecter les doublons.")
            return

    # Normalisation du nom pour comparaison insensible à la casse
    df["_norm_name"] = df["Name"].astype(str).str.strip().str.lower()

    doublons = []
    df_sorted = df.sort_values(by="_norm_name").reset_index()

    for i in range(len(df_sorted)):
        for j in range(i + 1, len(df_sorted)):
            row_i = df_sorted.loc[i]
            row_j = df_sorted.loc[j]

            # Si noms différents, on peut casser la boucle car trié par nom
            if row_j["_norm_name"] != row_i["_norm_name"]:
                break

            # Comparaison selon critères
            if (
                abs(row_i["Age"] - row_j["Age"]) <= 7
                and row_i["Gender"] == row_j["Gender"]
                and row_i["Blood Type"] == row_j["Blood Type"]
                and row_i["Doctor"] == row_j["Doctor"]
                and row_i["Hospital"] == row_j["Hospital"]
                and row_i["Billing Amount"] == row_j["Billing Amount"]
                and row_i["Date of Admission"] == row_j["Date of Admission"]
            ):
                doublons.append((row_i["Name"], row_i["Age"], row_j["Age"], row_i["Hospital"]))

    if doublons:
        print(f"⚠️ {len(doublons)} doublon(s) potentiel(s) détecté(s) :")
        for d in doublons[:10]:  # Affiche les 10 premiers
            print(f"   → {d[0]} (âges {d[1]} et {d[2]}) à {d[3]}")
        print("   → Recommandation : examiner et fusionner les doublons si nécessaire.")
    else:
        print("✅ Aucun doublon personnalisé détecté.")

    # Nettoyage colonne temporaire
    df.drop(columns=["_norm_name"], inplace=True, errors="ignore")




# === 7. Main ===
def main():
    print("=== 🧾 Vérification d'intégrité JSON avant migration MongoDB ===")

    df = charger_json(FICHIER_JSON)
    print(f"\n✅ Fichier chargé avec succès : {FICHIER_JSON}")
    print(f"→ {df.shape[0]} lignes, {df.shape[1]} colonnes")

    verifier_colonnes(df)
    verifier_valeurs_manquantes(df)
    verifier_types_mixtes(df)
    verifier_doublons_personnalises(df)

    print("\n🎯 Vérification terminée !")


if __name__ == "__main__":
    main()
