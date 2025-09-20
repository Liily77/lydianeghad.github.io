# scripts/nlp/nlp_step4_absa_light_fr.py
from pathlib import Path
import pandas as pd

PROC = Path("data/processed")
# Priorise le fichier avec influence ; sinon prend celui avec topics
IN = PROC / "avis_with_influence_fr.csv"
if not IN.exists():
    IN = PROC / "avis_with_topics_fr.csv"
    if not IN.exists():
        raise SystemExit("[ERR] Fichier d'entrée introuvable")

df = pd.read_csv(IN)

# Colonnes requises
for c in ["macro_topic","sentiment_z","avis"]:
    if c not in df.columns:
        raise SystemExit(f"[ERR] Colonne manquante: {c}")

# % d'avis influents si dispo
if "influence_score" in df.columns:
    thr = df["influence_score"].quantile(0.90)
    df["influential_flag"] = (df["influence_score"] >= thr).astype(int)
else:
    df["influential_flag"] = 0

n_total = len(df)

# --- synthèse par macro-thème
g = df.groupby("macro_topic", dropna=False)
summary = g.agg(
    n=("macro_topic","size"),
    mean_z=("sentiment_z","mean"),
    pct_influents=("influential_flag","mean"),
).reset_index()
summary["pct"] = summary["n"] / n_total
summary = summary.sort_values(["n","mean_z"], ascending=[False,False])
summary.to_csv(PROC/"absa_macro_summary_fr.csv", index=False, encoding="utf-8")

# --- matrices par hôtel (si la colonne existe)
if "hotel" in df.columns:
    counts = df.pivot_table(index="hotel", columns="macro_topic",
                            values="avis", aggfunc="count", fill_value=0).sort_index()
    meanz = df.pivot_table(index="hotel", columns="macro_topic",
                           values="sentiment_z", aggfunc="mean").sort_index()
    counts.to_csv(PROC/"absa_macro_by_hotel_counts_fr.csv", encoding="utf-8")
    meanz.to_csv(PROC/"absa_macro_by_hotel_mean_fr.csv",   encoding="utf-8")

# --- petits exemples +/− (utile pour le mémoire)
ex = []
for t, sub in df.groupby("macro_topic"):
    for side, block in [("pos", sub.sort_values("sentiment_z", ascending=False).head(3)),
                        ("neg", sub.sort_values("sentiment_z", ascending=True).head(3))]:
        for _, r in block.iterrows():
            ex.append({"macro_topic": t, "side": side, "hotel": r.get("hotel"),
                       "sentiment_z": r.get("sentiment_z"), "avis": r.get("avis")})
if ex:
    pd.DataFrame(ex).to_csv(PROC/"absa_examples_top_fr.csv", index=False, encoding="utf-8")

print("OK -> absa_macro_summary_fr.csv (+ matrices/exemples si dispo)")
