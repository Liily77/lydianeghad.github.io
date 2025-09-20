import pandas as pd
import re
import csv  # Pour quoting

# === 1. Charger les données ===
df = pd.read_csv("data/processed/avis_google_hotels.csv")
print(f"Données chargées : {df.shape[0]} lignes")

# === 2. Supprimer les colonnes inutiles ===
colonnes_supprimer = ['idreview', 'review_id', 'date']
for col in colonnes_supprimer:
    if col in df.columns:
        df.drop(columns=col, inplace=True)
        print(f"Colonne supprimée : {col}")

# === 3. Harmoniser types et valeurs ===

# Note → float
df['note'] = df['note'].astype(str).str.replace(',', '.', regex=False)
df['note'] = pd.to_numeric(df['note'], errors='coerce')

# Contributions → entier
df['contributions'] = df['contributions'].astype(str).str.extract(r'(\d+)')
df['contributions'] = pd.to_numeric(df['contributions'], errors='coerce').fillna(0).astype(int)

# Votes utiles (si présent)
if 'votes_utiles' in df.columns:
    df['votes_utiles'] = df['votes_utiles'].astype(str).str.extract(r'(\d+)')
    df['votes_utiles'] = pd.to_numeric(df['votes_utiles'], errors='coerce').fillna(0).astype(int)

# === 4. Nettoyage texte (avis, auteur) ===
def clean_text(text):
    text = str(text)
    text = text.replace('|', ' ')
    text = text.replace('…', '')
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

for col in ['avis', 'auteur']:
    if col in df.columns:
        df[col] = df[col].apply(clean_text)
        print(f"Colonne nettoyée : {col}")

# === 5. Supprimer les doublons ===
before = df.shape[0]
df.drop_duplicates(subset=['auteur', 'note', 'avis'], inplace=True)
after = df.shape[0]
print(f"Doublons supprimés : {before - after} ligne(s)")

# === 6. Sauvegarde CSV propre (quoting activé) ===
df.to_csv("data/processed/avis_google_hotels.csv", index=False, quoting=csv.QUOTE_ALL)
print("Fichier nettoyé sauvegardé dans data/processed/avis_google_hotels.csv")
