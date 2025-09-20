# scripts/platform/qa_curated.py
from pathlib import Path
import pandas as pd
import shutil, time

# --- chemins robustes depuis ce fichier ---
ROOT = Path(__file__).resolve().parents[2]
CUR  = ROOT / "data" / "curated"
CUR.mkdir(parents=True, exist_ok=True)

MAIN = CUR / "avis_with_influence_fr.csv"
if not MAIN.exists():
    raise SystemExit(f"[ERR] Fichier introuvable : {MAIN}")

# --- sauvegarde de sécurité ---
bkdir = CUR / "_backup"; bkdir.mkdir(exist_ok=True)
bk = bkdir / f"avis_with_influence_fr_{time.strftime('%Y%m%d-%H%M%S')}.csv"
shutil.copy2(MAIN, bk)

# --- lecture ---
df = pd.read_csv(MAIN)
n0 = len(df)

# 1) auteurs vides -> "Anonyme"
if "auteur" in df.columns:
    s = df["auteur"]
    s = s.fillna("").astype(str).str.strip()
    mask_empty = (s == "") | (s.str.lower().isin({"nan", "none"}))
    s = s.mask(mask_empty, "Anonyme")
    df["auteur"] = s

# 2) dates valides
if "date" in df.columns:
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

# 3) note numérique dans [1..5]
if "note" in df.columns:
    df["note"] = pd.to_numeric(df["note"], errors="coerce").clip(1, 5)

# 4) déduplication (hotel + auteur + date + note + avis)
keys = [k for k in ["hotel","auteur","date","note","avis"] if k in df.columns]
n_dup = 0
if keys:
    before = len(df)
    df = df.drop_duplicates(subset=keys, keep="first")
    n_dup = before - len(df)

# 5) avis non vides
n_empty = 0
if "avis" in df.columns:
    before = len(df)
    avis = df["avis"].fillna("").astype(str).str.strip()
    df = df[avis != ""].copy()
    n_empty = before - len(df)

# --- écriture ---
df.to_csv(MAIN, index=False, encoding="utf-8")

# --- petit rapport texte ---
rep = CUR / "QA_report.txt"
rep.write_text(
    "QA sur avis_with_influence_fr.csv\n"
    f"- lignes initiales : {n0}\n"
    f"- doublons supprimés : {n_dup}\n"
    f"- avis vides supprimés : {n_empty}\n"
    f"- lignes finales : {len(df)}\n",
    encoding="utf-8"
)

print("✔ QA terminée")
print("  sauvegarde  ->", bk)
print("  fichier OK  ->", MAIN)
print("  rapport     ->", rep)
