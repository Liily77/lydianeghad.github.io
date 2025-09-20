# scripts/nlp/nlp_step2_topics_fr.py
# Objectif : extraire des thèmes (TF-IDF + NMF) sur le corpus FR uniquement + fusion macro-thèmes.

import os, re
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF

# --- Chemins (identiques à tout à l'heure) ---
IN_PATH  = "../../data/processed/avis_with_sentiment_fr.csv"
OUT_PATH = "../../data/processed/avis_with_topics_fr.csv"   # même fichier qu'avant
REPORT   = "../../data/processed/topics_report_fr.txt"      # même fichier qu'avant
STOP_TXT = "../../resources/stopwords/stopwords-fr.txt"     # ton fichier téléchargé

# --- Nettoyage texte simple (minuscules, pas d’URL, espaces propres) ---
def clean(s: str) -> str:
    s = str(s).lower()
    s = re.sub(r"http\S+|www\S+", " ", s)
    s = re.sub(r"[^a-zàâäéèêëîïôöùûüç'\s-]", " ", s)
    return re.sub(r"\s+", " ", s).strip()

# --- Top mots d’un thème (pour libeller) ---
def show_topics(model, feat_names, topn=10):
    out = []
    for tid, row in enumerate(model.components_):
        top = row.argsort()[-topn:][::-1]
        out.append((tid, [feat_names[j] for j in top]))
    return out

# --- Choix automatique du nombre de thèmes ---
def pick_k(n_docs: int) -> int:
    import math
    return max(4, min(12, int(math.sqrt(max(1, n_docs) / 10))))

# --- (Option) filtre les réponses “officielles” de l’hôtel ---
def is_owner_reply(t: str) -> bool:
    t = (t or "").lower()
    keys = ["cher client","chère cliente","nous vous remercions","merci pour votre",
            "notre établissement","votre séjour","espérons vous revoir","best western"]
    return any(k in t for k in keys)

def main():
    if not os.path.exists(IN_PATH):
        raise FileNotFoundError(IN_PATH)

    # 1) Charger + préparer
    df = pd.read_csv(IN_PATH)
    if "avis" not in df.columns:
        raise ValueError("Colonne 'avis' manquante.")
    df = df[~df["avis"].astype(str).apply(is_owner_reply)].reset_index(drop=True)
    df["avis_clean"] = df["avis"].astype(str).apply(clean)
    df = df[df["avis_clean"].str.len() > 0].reset_index(drop=True)
    print("Avis FR préparés :", len(df))

    # 2) Stopwords : charge ton fichier si présent, sinon None
    if os.path.exists(STOP_TXT):
        with open(STOP_TXT, "r", encoding="utf-8-sig") as f:
            stop = sorted({w.strip().lower() for w in f if w.strip() and not w.strip().startswith("#")})
        print(f"Stopwords chargés ({len(stop)}) depuis {STOP_TXT}")
    else:
        stop = None
        print("Pas de stopwords fichier → stop_words=None (OK pour une V1)")

    # 3) TF-IDF (mots + bigrammes)
    vect = TfidfVectorizer(
        max_features=8000, min_df=3, max_df=0.6,
        ngram_range=(1,2), stop_words=stop, token_pattern=r"(?u)\b\w\w+\b"
    )
    X = vect.fit_transform(df["avis_clean"])
    if X.shape[1] == 0:
        raise RuntimeError("Vocabulaire vide (stoplist trop agressive ?)")

    # 4) NMF (décomposition en thèmes)
    k = 10
    nmf = NMF(n_components=k, init="nndsvd", random_state=42, max_iter=400)
    W = nmf.fit_transform(X)
    feat = vect.get_feature_names_out()

    topics = show_topics(nmf, feat, topn=10)
    labels = {tid: ", ".join(words[:4]) for tid, words in topics}  # étiquette courte

    # 5) Affecter le thème dominant à chaque avis
    df["topic_id"] = W.argmax(axis=1)
    df["topic_score"] = W.max(axis=1)
    df["topic_label"] = df["topic_id"].map(labels)

    # 5bis) FUSION en macro-thèmes (0+6), (3+4), (5+7)
    MAP = {
        0:"Localisation / Transports", 6:"Localisation / Transports",
        1:"Rapport qualité-prix",
        2:"Petit-déjeuner",
        3:"Chambre / Confort", 4:"Chambre / Confort",
        5:"Accueil / Service", 7:"Accueil / Service",
        8:"Salle de bain",
        9:"Propreté",
    }
    df["macro_topic"] = df["topic_id"].map(MAP).fillna("Autres")

    # 6) Sauvegardes + rapport (on complète le même rapport)
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    df.to_csv(OUT_PATH, index=False, encoding="utf-8")

    # Prépare un rapport un peu plus riche
    rep_lines = [f"k={k}"] + [f"Topic {t}: " + ", ".join(ws) for t, ws in topics]
    # Résumé macro-thèmes (répartition + sentiment moyen si dispo)
    rep_lines += ["", "== Macro-thèmes (répartition) =="]
    tot = len(df)
    counts = df["macro_topic"].value_counts()
    for m, n in counts.items():
        rep_lines.append(f"{m}: {n} ({n/tot:.1%})")
    if "sentiment_z" in df.columns:
        rep_lines += ["", "== Sentiment moyen par macro-thème (−1→+1) =="]
        s = df.groupby("macro_topic")["sentiment_z"].mean().sort_values()
        for m, v in s.items():
            rep_lines.append(f"{m}: {v:.3f}")

    with open(REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(rep_lines))

    print(f"✅ Sauvé : {OUT_PATH}")
    print(f"📝 Rapport : {REPORT}")
    print(df[["topic_id","topic_label","macro_topic","topic_score"]].head(10).to_string(index=False))

if __name__ == "__main__":
    main()
