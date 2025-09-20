# scripts/nlp/nlp_step0_lang_detect.py
# Objectif : détecter la langue, l'afficher, puis garder une version "FR uniquement".

import os
import pandas as pd
from langdetect import detect, DetectorFactory

IN_PATH   = "../../data/processed/avis_with_sentiment.csv"
OUT_PATH  = "../../data/processed/avis_with_sentiment.csv"          # réécrit avec 'langue'
FR_OUT    = "../../data/processed/avis_with_sentiment_fr.csv"       # nouveau fichier FR-only

DetectorFactory.seed = 0

def detect_lang_safe(text: str, min_chars: int = 20) -> str:
    s = str(text or "").strip()
    if len(s) < min_chars:
        return "unk"
    try:
        return detect(s).lower()
    except Exception:
        return "unk"

def main():
    if not os.path.exists(IN_PATH):
        raise FileNotFoundError(IN_PATH)

    df = pd.read_csv(IN_PATH)
    if "avis" not in df.columns:
        raise ValueError("Colonne 'avis' manquante dans le CSV.")

    print(f"📥 Avis chargés : {len(df)}")
    df["langue"] = df["avis"].apply(detect_lang_safe)

    # Aperçus rapides
    print("\n🔎 20 premières valeurs de 'langue' :")
    print(df["langue"].head(20).to_string(index=False))

    print("\n🧩 Extrait (langue + début d'avis) :")
    print(
        df.assign(avis_preview=df["avis"].astype(str).str.slice(0, 80))
          [["langue", "avis_preview"]]
          .head(10)
          .to_string(index=False)
    )

    # Répartition globale
    counts = df["langue"].value_counts()
    total = len(df)
    print("\n🌍 Répartition des langues :")
    for lg, n in counts.items():
        print(f" - {lg}: {n} ({n/total:.2%})")
    print("('unk' = avis trop court ou non détectable)")

    # Sauvegarde (fichier complet avec 'langue')
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    df.to_csv(OUT_PATH, index=False, encoding="utf-8")
    print(f"\n✅ Sauvé (avec 'langue') → {OUT_PATH}")

    # ➜ Version FR uniquement (pour les thèmes)
    df_fr = df[df["langue"] == "fr"].reset_index(drop=True)
    df_fr.to_csv(FR_OUT, index=False, encoding="utf-8")
    print(f"✅ Sauvé (FR uniquement) → {FR_OUT}  ({len(df_fr)}/{total} = {len(df_fr)/total:.2%})")

if __name__ == "__main__":
    main()
