# scripts/platform/check_dups_raw.py
import sys, pandas as pd
from pathlib import Path

if len(sys.argv) < 2:
    print("Usage: python scripts/platform/check_dups_raw.py <chemin_csv_raw>")
    sys.exit(1)

path = Path(sys.argv[1])
df = pd.read_csv(path, encoding="utf-8")

key = ["auteur", "note", "date", "avis"]
missing = [c for c in key if c not in df.columns]
if missing:
    print(f"[ERR] Colonnes manquantes pour la clé: {missing}")
    print(f"Colonnes disponibles: {list(df.columns)}")
    sys.exit(2)

dups = df.duplicated(subset=key, keep="first")
print(f"Fichier: {path}")
print(f"- Lignes totales : {len(df)}")
print(f"- Doublons (clé auteur,note,date,avis) : {int(dups.sum())}")

# Montre quelques exemples de doublons s'il y en a
if dups.any():
    print("\nExemples de doublons (5) :")
    print(df.loc[dups, key].head(5).to_string(index=False))
