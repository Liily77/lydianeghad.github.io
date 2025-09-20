# scripts/nlp/nlp_step3_influence_fr.py
from pathlib import Path
import pandas as pd
import numpy as np
import re
import argparse

# --------------------------- CLI ---------------------------
ap = argparse.ArgumentParser(description="Score d'influence (review-level)")
ap.add_argument("--in",  dest="inp",  default="../../data/processed/avis_with_topics_fr.csv",
                help="CSV d'entrée (par défaut: avis_with_topics_fr.csv)")
ap.add_argument("--out", dest="out",  default="../../data/processed/avis_with_influence_fr.csv",
                help="CSV de sortie (par défaut: avis_with_influence_fr.csv)")
ap.add_argument("--pctl", type=float, default=0.90,
                help="quantile pour définir 'influents' (défaut 0.90 = top 10%)")
ap.add_argument("--wlen", type=float, default=0.4, help="poids longueur")
ap.add_argument("--wemo", type=float, default=0.4, help="poids intensité émotionnelle |z|")
ap.add_argument("--wtop", type=float, default=0.2, help="poids topic_score")
args = ap.parse_args()

IN  = Path(args.inp)
OUT = Path(args.out)
if not IN.exists():
    raise SystemExit(f"[ERR] Fichier d'entrée introuvable: {IN}")

df = pd.read_csv(IN)

# ---------------------- contrôles colonnes -----------------
need_cols = ["avis", "sentiment_z"]
for c in need_cols:
    if c not in df.columns:
        raise SystemExit(f"[ERR] Colonne manquante: {c}. Exécute d'abord le sentiment/topics.")
# topic_score est optionnel (0 si absent)
if "topic_score" not in df.columns:
    df["topic_score"] = 0.0

# -------------------- fonctions utilitaires ----------------
def n_words(txt: str) -> int:
    # compte simple des tokens alphanumériques
    return len(re.findall(r"\w+", str(txt))) if pd.notna(txt) else 0

def norm01(s: pd.Series) -> pd.Series:
    s = pd.to_numeric(s, errors="coerce")
    vmin, vmax = s.min(skipna=True), s.max(skipna=True)
    if pd.isna(vmin) or pd.isna(vmax) or vmax == vmin:
        return pd.Series(np.zeros(len(s)), index=s.index)
    return (s - vmin) / (vmax - vmin)

# -------------------- calcul des features ------------------
df["nb_mots"] = df["avis"].apply(n_words)
longueur_norm = norm01(df["nb_mots"])
emo_abs_norm  = norm01(df["sentiment_z"].abs())
topic_norm    = norm01(df["topic_score"])

# --------------------- score d'influence -------------------
wL, wE, wT = args.wlen, args.wemo, args.wtop
df["influence_score"] = wL*longueur_norm + wE*emo_abs_norm + wT*topic_norm

# seuil top-k %
thr = df["influence_score"].quantile(args.pctl)
df["influential_flag"] = (df["influence_score"] >= thr).astype(int)

# ------------------------ sauvegarde -----------------------
OUT.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUT, index=False, encoding="utf-8")

# ----------------------- résumé console --------------------
share = df["influential_flag"].mean()
print(f"✔ Influence -> {OUT}")
print(f"   lignes: {len(df)} | seuil q={args.pctl:.2f}: {thr:.4f} | part influents: {share:.1%}")
print("   colonnes ajoutées: nb_mots, influence_score, influential_flag")
