# scripts/nlp/author_centrality.py
from pathlib import Path
import pandas as pd

# --- chemins robustes (depuis l'emplacement du fichier) ---
ROOT = Path(__file__).resolve().parents[2]
PROC = ROOT / "data" / "processed"
IN   = PROC / "avis_with_influence_fr.csv"
OUTG = PROC / "centralite_auteur_global.csv"
OUTH = PROC / "centralite_auteur_par_hotel.csv"

if not IN.exists():
    raise SystemExit(f"[ERR] Fichier introuvable : {IN}")

df = pd.read_csv(IN)

# --- colonnes indispensables ---
if "auteur" not in df.columns:
    raise SystemExit("[ERR] Colonne 'auteur' manquante")
if "influence_score" not in df.columns:
    raise SystemExit("[ERR] Colonne 'influence_score' manquante (exécute d'abord nlp_step3_influence_fr.py)")

# Nettoyage auteur
df["auteur"] = df["auteur"].astype(str).str.strip()
df.loc[df["auteur"].isna() | (df["auteur"] == "") | (df["auteur"].str.lower() == "nan"), "auteur"] = "Anonyme"

# Helper: retourne une Series (même longueur) même si la colonne n'existe pas
def col_or_empty(name: str) -> pd.Series:
    return df[name].astype(str) if name in df.columns else pd.Series([""] * len(df), index=df.index)

# review_id de secours si absent (concat de plusieurs champs)
if "review_id" not in df.columns or df["review_id"].isna().all():
    df["review_id"] = (
        col_or_empty("hotel") + "|" +
        df["auteur"].astype(str) + "|" +
        col_or_empty("date")  + "|" +
        col_or_empty("note")
    )

# --- centralité globale (tous hôtels) ---
grp = df.groupby("auteur", dropna=False).agg(
    n_avis=("review_id", "nunique"),
    score_moy=("influence_score", "mean"),
    score_max=("influence_score", "max"),
).reset_index()

# score de centralité simple (pondère qualité + volume)
grp["centralite"] = (
    grp["score_moy"].rank(pct=True) * 0.6 +
    grp["n_avis"].rank(pct=True)    * 0.4
)
grp = grp.sort_values("centralite", ascending=False)
grp.to_csv(OUTG, index=False, encoding="utf-8")

# --- centralité par hôtel ---
if "hotel" in df.columns:
    grp_h = df.groupby(["hotel", "auteur"], dropna=False).agg(
        n_avis=("review_id", "nunique"),
        score_moy=("influence_score", "mean"),
        score_max=("influence_score", "max"),
    ).reset_index()

    grp_h["centralite"] = (
        grp_h["score_moy"].rank(method="dense", pct=True) * 0.6 +
        grp_h["n_avis"].rank(method="dense", pct=True)    * 0.4
    )
    grp_h = grp_h.sort_values(["hotel", "centralite"], ascending=[True, False])
    grp_h.to_csv(OUTH, index=False, encoding="utf-8")

print("✔ Centralité calculée")
print("  ->", OUTG)
if "hotel" in df.columns:
    print("  ->", OUTH)
