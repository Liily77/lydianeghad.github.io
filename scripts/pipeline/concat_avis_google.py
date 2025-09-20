from pathlib import Path
import pandas as pd

BASE_DIR      = Path(__file__).resolve().parents[2]
RAW_DIR       = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
OUT_PATH      = PROCESSED_DIR / "avis_google_hotels.csv"

def main():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    frames = []
    all_cols = set()
    for p in sorted(RAW_DIR.glob("avis_google_*.csv")):
        df = pd.read_csv(p, dtype=str, encoding="utf-8")
        df["hotel"] = p.stem.replace("avis_google_", "")
        frames.append(df)
        all_cols |= set(df.columns)

    all_cols = sorted(all_cols | {"hotel"})
    frames = [f.reindex(columns=all_cols) for f in frames]

    merged = pd.concat(frames, ignore_index=True)
    merged.to_csv(OUT_PATH, index=False, encoding="utf-8")
    print(f"✅ Fusion OK → {OUT_PATH.relative_to(BASE_DIR)} ({len(merged)} lignes)")

if __name__ == "__main__":
    main()
