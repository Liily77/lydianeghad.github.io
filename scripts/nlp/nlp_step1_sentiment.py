#------Importations

import os
import math
import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline


IN_PATH  = "../../data/processed/avis_google_hotels.csv"
OUT_PATH = "../../data/processed/avis_with_sentiment.csv"
MODEL    = "nlptown/bert-base-multilingual-uncased-sentiment"

def load_df(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Introuvable: {path}")
    df = pd.read_csv(path)
    if "avis" not in df.columns:
        raise ValueError("La colonne 'avis' est manquante dans le CSV.")
    # Texte en string, valeurs manquantes -> ""
    df["avis"] = df["avis"].fillna("").astype(str)
    # Option: filtre (éviter les lignes vides)
    df = df[df["avis"].str.strip().str.len() > 0].reset_index(drop=True)
    return df

def build_pipeline(model_name: str):
    print(f"Chargement du modèle {model_name} ...")
    # (facultatif) limiter les threads CPU si tu veux
    try:
        torch.set_num_threads(max(1, os.cpu_count() // 2))
    except Exception:
        pass

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    pipe = pipeline(
        task="sentiment-analysis",
        model=model,
        tokenizer=tokenizer,
        device=-1,                # CPU
        truncation=True,          # coupe au-delà de 512 tokens
        max_length=512,
        batch_size=16             # ajuste (8–32) selon la machine
    )
    print("Modèle prêt")
    return pipe

def stars_to_num(label: str) -> int:
    # "1 star" / "2 stars" ... -> entier 1..5
    import re
    m = re.search(r"(\d)", str(label))
    return int(m.group(1)) if m else 3

def num_to_polarity(n: int) -> str:
    #  1–2 = neg, 3 = neutre, 4–5 = pos
    if n <= 2: return "neg"
    if n == 3: return "neu"
    return "pos"

def main():

    # 1) Charge les données

    df = load_df(IN_PATH)
    print(f"Avis chargés: {len(df)}")

    # 2) Pipeline

    pipe = build_pipeline(MODEL)

    # 3) Prédire par batch 

    texts = df["avis"].tolist()
    print("Inférence sur le corpus...")
    results = pipe(texts)  # batch géré en interne

    # 4) Ajouter colonnes

    df["sentiment_label"] = [r["label"] for r in results]
    df["sentiment_score"] = [float(r["score"]) for r in results]
    df["sentiment_num"]   = df["sentiment_label"].apply(stars_to_num).astype(int)

    # normalisation -1..+1 : (1→-1, 3→0, 5→+1)

    df["sentiment_z"]     = (df["sentiment_num"] - 3) / 2
    df["sentiment_polarity"] = df["sentiment_num"].apply(num_to_polarity)

    # 5) Sauvegarde

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    df.to_csv(OUT_PATH, index=False, encoding="utf-8")
    print(f" Sauvegardé → {OUT_PATH}")
    print("\nAperçu :")
    print(df[["avis", "sentiment_label", "sentiment_num", "sentiment_z", "sentiment_polarity"]].head(8))

    # 6) Quelques stats utiles en console

    print("\n Répartition (1–5 étoiles) :")
    print(df["sentiment_num"].value_counts().sort_index())
    print("\n Répartition (neg/neu/pos) :")
    print(df["sentiment_polarity"].value_counts())

if __name__ == "__main__":
    main()
