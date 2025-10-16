"""
Script : check_integrity.py
But : Vérifier l'intégrité d'un fichier de données avant migration vers MongoDB
Auteur : GPT-5 (Assistant Python)
"""

import pandas as pd
import numpy as np
import os
import sys

# === CONFIGURATION ===
FICHIER = "healthcare_dataset_purge.csv"  # Nom du fichier à tester (CSV ou XLSX)
# csv_file_path = '../data/healthcare_dataset_purge.csv'

def charger_fichier(fichier):
    """Charge un fichier CSV ou Excel et retourne un DataFrame pandas."""
    if not os.path.exists(fichier):
        print(f"❌ Erreur : Le fichier '{fichier}' est introuvable.")
        sys.exit(1)

    try:
        if fichier.endswith(".csv"):
            df = pd.read_csv(fichier)
        elif fichier.endswith((".xls", ".xlsx")):
            df = pd.read_excel(fichier)
        else:
            print("❌ Format non supporté. Utilise un fichier CSV ou Excel.")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur lors du chargement du fichier : {e}")
        sys.exit(1)
    return df


def verifier_colonnes(df):
    """Affiche la liste des colonnes et leur type."""
    print("\n📊 Colonnes disponibles et types de données :")
    print(df.dtypes)
    print(f"\nNombre total de colonnes : {len(df.columns)}")


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


def verifier_doublons(df):
    """Vérifie les doublons dans le DataFrame."""
    print("\n🧬 Vérification des doublons :")
    duplicates = df.duplicated().sum()
    if duplicates == 0:
        print("✅ Aucun doublon détecté.")
    else:
        print(f"⚠️ {duplicates} doublon(s) détecté(s).")
        print("   → Recommandation : supprimer via df.drop_duplicates(inplace=True)")


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


def generer_recommandations(df):
    """Fournit des recommandations avant migration MongoDB."""
    print("\n🧠 Recommandations avant migration vers MongoDB :")
    print("""
✅ 1. Nettoyer les valeurs manquantes (remplacer, supprimer ou normaliser)
✅ 2. Supprimer les doublons
✅ 3. S'assurer que les colonnes clés sont uniques
✅ 4. Convertir les types incompatibles (dates, booléens, nombres)
✅ 5. Vérifier l'encodage UTF-8 pour éviter les caractères illisibles
✅ 6. Exporter le fichier final en JSON pour import MongoDB :
       df.to_json('data_clean.json', orient='records', lines=True)
    """)


def main():
    print("=== 🧾 Test d'intégrité des données avant migration MongoDB ===")

    df = charger_fichier(FICHIER)
    print(f"\n✅ Fichier chargé avec succès : {FICHIER}")
    print(f"→ {df.shape[0]} lignes, {df.shape[1]} colonnes")

    verifier_colonnes(df)
    verifier_valeurs_manquantes(df)
    verifier_doublons(df)
    verifier_types_mixtes(df)
    generer_recommandations(df)

    print("\n🎯 Vérification terminée !")


if __name__ == "__main__":
    main()
