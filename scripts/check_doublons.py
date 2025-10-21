"""
Script : purge_healthcare_data_auto.py
But : Détecter et traiter automatiquement les doublons du dataset santé.
      - Si Medical Condition ou Date of Admission diffèrent → suppression des deux lignes.
      - Sinon → fusion avec âge = moyenne arrondie à l'entier supérieur.
Auteur : GPT-5 (Assistant Python)
"""

import pandas as pd
import numpy as np
import math
import os

FICHIER_ENTREE = "healthcare_dataset.csv"
FICHIER_SORTIE = "healthcare_dataset_purge.csv"


def charger_fichier(fichier):
    """Charge le fichier CSV et retourne un DataFrame."""
    if not os.path.exists(fichier):
        print(f"❌ Fichier introuvable : {fichier}")
        exit(1)

    df = pd.read_csv(fichier)
    print(f"✅ Fichier chargé : {fichier} ({len(df)} lignes)")
    return df


def normaliser_texte(val):
    """Convertit en minuscule et supprime les espaces pour comparaison robuste."""
    if pd.isna(val):
        return ""
    return str(val).strip().lower()


def sont_doublons(row1, row2):
    """
    Vérifie si deux lignes sont des doublons selon les règles.
    Un doublon est défini par :
    - même Name (insensible à la casse)
    - Age à ±7 ans
    - même Gender, Blood Type, Doctor, Hospital, Billing Amount, Date of Admission
    """
    try:
        same_name = normaliser_texte(row1["Name"]) == normaliser_texte(row2["Name"])
        same_gender = normaliser_texte(row1["Gender"]) == normaliser_texte(row2["Gender"])
        same_blood = normaliser_texte(row1["Blood Type"]) == normaliser_texte(row2["Blood Type"])
        same_doctor = normaliser_texte(row1["Doctor"]) == normaliser_texte(row2["Doctor"])
        same_hospital = normaliser_texte(row1["Hospital"]) == normaliser_texte(row2["Hospital"])
        same_billing = abs(float(row1["Billing Amount"]) - float(row2["Billing Amount"])) < 0.01
        same_admission = normaliser_texte(row1["Date of Admission"]) == normaliser_texte(row2["Date of Admission"])

        age_close = abs(float(row1["Age"]) - float(row2["Age"])) <= 7

        return all([
            same_name, same_gender, same_blood, same_doctor,
            same_hospital, same_billing, same_admission, age_close
        ])
    except Exception as e:
        print(f"⚠️ Erreur comparaison : {e}")
        return False


def fusion_ou_suppression(row1, row2):
    """
    Si Medical Condition ou Date of Admission diffèrent → supprimer les deux lignes.
    Sinon → fusionner (moyenne de l'âge arrondie à l'entier supérieur).
    """
    condition_diff = normaliser_texte(row1["Medical Condition"]) != normaliser_texte(row2["Medical Condition"])
    admission_diff = normaliser_texte(row1["Date of Admission"]) != normaliser_texte(row2["Date of Admission"])

    if condition_diff or admission_diff:
        print(f"🗑️ Suppression : {row1['Name']} (diagnostic ou date différents)")
        return None

    # Sinon fusionner
    age1 = float(row1["Age"])
    age2 = float(row2["Age"])
    age_moy = math.ceil(np.mean([age1, age2]))  # arrondi à l'entier supérieur

    merged = row1.copy()
    merged["Age"] = int(age_moy)
    print(f"🔗 Fusion : {row1['Name']} → Âge fusionné = {age_moy}")
    return merged


def traiter_doublons(df):
    """Traite automatiquement les doublons."""
    processed_indices = set()
    result_rows = []
    doublon_compteur = 0
    fusion_compteur = 0
    suppression_compteur = 0

    for i, row1 in df.iterrows():
        if i in processed_indices:
            continue

        doublon_trouve = False
        for j, row2 in df.iloc[i + 1:].iterrows():
            if sont_doublons(row1, row2):
                doublon_trouve = True
                doublon_compteur += 1
                processed_indices.add(j)

                merged = fusion_ou_suppression(row1, row2)
                if merged is not None:
                    fusion_compteur += 1
                    result_rows.append(merged)
                else:
                    suppression_compteur += 1
                break  # Passe au doublon suivant

        if not doublon_trouve:
            result_rows.append(row1)

        processed_indices.add(i)

    print("\n=== Résumé du traitement ===")
    print(f"🔎 Doublons détectés : {doublon_compteur}")
    print(f"🔗 Fusions effectuées : {fusion_compteur}")
    print(f"🗑️ Suppressions effectuées : {suppression_compteur}")
    print("============================\n")

    return pd.DataFrame(result_rows)


def main():
    print("=== 🏥 Nettoyage automatique du fichier healthcare_dataset.csv ===\n")
    df = charger_fichier(FICHIER_ENTREE)

    # Vérification colonnes nécessaires
    colonnes_requises = [
        "Name", "Age", "Gender", "Blood Type", "Date of Admission",
        "Doctor", "Hospital", "Billing Amount", "Medical Condition"
    ]
    manquantes = [c for c in colonnes_requises if c not in df.columns]
    if manquantes:
        print(f"❌ Colonnes manquantes : {manquantes}")
        exit(1)

    df_result = traiter_doublons(df)

    # Sauvegarde du résultat final
    df_result.to_csv(FICHIER_SORTIE, index=False)
    print(f"✅ Fichier final enregistré : {FICHIER_SORTIE}")
    print(f"→ {len(df_result)} lignes conservées sur {len(df)} initiales.")
    print("\n👋 Programme terminé avec succès.")


if __name__ == "__main__":
    main()
