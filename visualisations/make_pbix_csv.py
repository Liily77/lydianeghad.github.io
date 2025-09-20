#!/usr/bin/env python3
import argparse
import re
from pathlib import Path
import pandas as pd

TECH_COLS = [
    "nb_avis_total","note_moyenne","sentiment_label","sentiment_polarity",
    "avis_clean","topic_label","sentiment_score","sentiment_num"
]
DECIMAL_COLS = ["note","topic_score","sentiment_z","influence_score"]
INT_COLS     = ["contributions","topic_id","nb_mots","influential_flag"]
TEXT_COLS    = ["hotel","auteur","langue","macro_topic","avis"]
ORDER        = [
    "hotel","auteur","contributions","langue",
    "macro_topic","topic_id","topic_score",
    "nb_mots","note","sentiment_z","influence_score",
    "influential_flag","avis","date"
]

def _to_float(x):
    if pd.isna(x):
        return pd.NA
    s = str(x).strip()
    s = s.replace("\u202f"," ").replace("\xa0"," ").replace(" ","")
    s = s.replace(",",".")
    s = re.sub(r"[^0-9.\-]","",s)
    if s in {"",".","-","-.",".-"}:
        return pd.NA
    try:
        return float(s)
    except Exception:
        return pd.NA

def _to_int(x):
    if pd.isna(x):
        return pd.NA
    s = str(x).strip()
    s = s.replace("\u202f"," ").replace("\xa0"," ").replace(" ","")
    s = re.sub(r"[^0-9\-]","",s)
    if s in {"","-"}:
        return pd.NA
    try:
        return int(s)
    except Exception:
        return pd.NA

def main(input_path: Path=None, output_path: Path=None, encoding="utf-8", fr_csv=False):
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent

    if input_path is None:
        candidates = [
            project_root/"data"/"curated"/"avis_with_influence_fr.csv",
            project_root/"data"/"processed"/"avis_with_influence_fr.csv",
            script_dir/"avis_with_influence_fr.csv",
        ]
        for c in candidates:
            if c.exists():
                input_path = c
                break
    if input_path is None or not input_path.exists():
        raise SystemExit("[ERR] Fichier d'entrée introuvable. Passez un chemin avec --input")

    if output_path is None:
        output_path = script_dir/"avis_with_influence_fr_pbix.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"🔎 Lecture : {input_path}")
    df = pd.read_csv(input_path, dtype=str, encoding=encoding)

    # Supprimer colonnes techniques si présentes
    drop_list = [c for c in TECH_COLS if c in df.columns]
    if drop_list:
        df = df.drop(columns=drop_list)
        print(f"🧹 Colonnes supprimées : {drop_list}")
    else:
        print("🧹 Aucune colonne technique à supprimer.")

    # Types
    for c in DECIMAL_COLS:
        if c in df.columns:
            df[c] = df[c].apply(_to_float).astype("Float64")
    for c in INT_COLS:
        if c in df.columns:
            df[c] = df[c].apply(_to_int).astype("Int64")
    for c in TEXT_COLS:
        if c in df.columns:
            df[c] = df[c].astype(str).str.strip()
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce", dayfirst=True)

    # Ordre recommandé
    ordered = [c for c in ORDER if c in df.columns]
    rest = [c for c in df.columns if c not in ordered]
    df = df[ordered + rest]

    # Écriture : mode FR (auto-typage PBI) ou standard
    sep = ","
    if fr_csv:
        # décimales -> texte avec virgule (NaN -> vide)
        for c in DECIMAL_COLS:
            if c in df.columns:
                df[c] = df[c].astype("Float64")
                df[c] = df[c].map(lambda v: "" if pd.isna(v) else str(v).replace(".", ","))
        sep = ";"

    df.to_csv(output_path, index=False, encoding=encoding, sep=sep)
    print(f"✅ Écrit : {output_path}")
    print(f"   Lignes: {len(df):,} | Colonnes: {len(df.columns)} | sep='{sep}' | fr_csv={fr_csv}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--input","-i", type=Path, default=None)
    ap.add_argument("--output","-o", type=Path, default=None)
    ap.add_argument("--encoding", default="utf-8")
    ap.add_argument("--fr-csv", action="store_true",
                    help="CSV FR: séparateur ';' + décimales avec virgule (typage auto dans Power BI FR)")
    args = ap.parse_args()
    main(args.input, args.output, args.encoding, fr_csv=args.fr_csv)
