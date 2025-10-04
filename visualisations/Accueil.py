# -*- coding: utf-8 -*-
"""
Accueil Streamlit : bannière image + intro + chargement CSV + filtres + aperçu propre.
"""

from pathlib import Path
from base64 import b64encode
import pandas as pd
import streamlit as st

# Ouvre la sidebar + style Best Western (bleu + textes jaunes)
st.set_page_config(
    page_title=st.get_option("browser.gatherUsageStats") and "BW Paris" or "BW Paris",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
  /* Fond bleu foncé de la sidebar */
  [data-testid="stSidebar"]{
    background: linear-gradient(180deg,#0F2F57 0%, #153E75 55%, #1C4F8C 100%) !important;
    border-right: 1px solid rgba(0,0,0,.15);
  }
  /* Couleur des textes/liens de navigation en jaune */
  [data-testid="stSidebar"] *, 
  [data-testid="stSidebar"] a{
    color: #FFD34E !important;            /* jaune doré lisible */
    text-decoration: none !important;
  }
  /* Petites pastilles/icônes */
  [data-testid="stSidebar"] svg{ fill: #FFD34E !important; }
</style>
""", unsafe_allow_html=True)


# --- Utils images -------------------------------------------------------------

def _b64(path: str) -> str:
    """Lit un fichier binaire et renvoie sa base64 ('' si absent)."""
    p = Path(path)
    return b64encode(p.read_bytes()).decode("utf-8") if p.exists() else ""

# --- Habillage : bannière + bande bleue --------------------------------------

_banner_b64 = _b64("visualisations/banner_bw.PNG")
_logo_b64   = _b64("visualisations/logo_bw.png")



st.markdown(f"""
<style>
  .main .block-container {{
    border-left: 6px solid #153E75; padding-left: 16px; padding-top: .25rem;
  }}
  .hero-banner {{
    position: relative; height: 180px; border-radius: 14px;
    margin: 6px 0 12px 0; overflow: hidden;
    background: linear-gradient(90deg, #153E75, #1C4F8C);
  }}
  .hero-banner .hero-bg {{
    position: absolute; inset: 0;
    background-image: url('data:image/png;base64,{_banner_b64}');
    background-size: cover; background-position: center;
    filter: blur(1.5px);              /* + de flou sur l'image */
    transform: scale(1.03);
  }}
  /* Dégradé bleu existant (fond) */
  .hero-banner::before {{
    content: ""; position: absolute; inset: 0; z-index: 0;
    background: linear-gradient(90deg,
      rgba(21,62,117,.85) 0%,
      rgba(28,79,140,.65) 45%,
      rgba(15,47,87,.55) 100%);
  }}
  /* Voile noir semi-transparent au-dessus (relief du texte) */
  .hero-banner::after {{
    content: ""; position: absolute; inset: 0; z-index: 1;
    background: rgba(0,0,0,.35);      /* ajuste l’opacité si besoin (.30–.50) */
  }}
  .hero-content {{
    position: relative; z-index: 2; color: #fff;
    display: flex; align-items: center; gap: 14px; padding: 18px 22px;
  }}
  .hero-logo {{ height: 56px; background: #fff; border-radius: 10px; padding: 6px; }}
  .hero-content h1 {{ margin: 0; font-size: 1.4rem; }}
  .hero-content p {{ margin: .25rem 0 0 0; opacity: .97; }}
</style>

<div class="hero-banner">
  <div class="hero-bg"></div>
  <div class="hero-content">
    <img class="hero-logo" src="data:image/png;base64,{_logo_b64}" alt="Best Western">
    <div>
      <h1>Best Western — Influence & Centralité</h1>
      <p>4 hôtels Best Western à <b>Paris.</b> La détection des clients influents à partir des avis Google, supervision par hôtel et par thème.</p>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<h3 style="color:#153E75;">Contexte & objectif</h3>', unsafe_allow_html=True)

st.markdown("Nous analysons les avis Google de **4 hôtels Best Western à Paris** ")
st.markdown("Objectif : **repérer rapidement les avis et clients qui pèsent le plus**. ")
st.markdown("Nous résumons ces retours en repères simples comme les nombre d’avis, ressenti, thèmes, impact "
    "pour aider à décider où agir en priorité, hôtel par hôtel.")


# Abréviations → nom & adresse (codes des CSV)
st.markdown(
    "- **BW_Ronceray_Opera** = Best Western Ronceray Opéra \n"
    "- **BW_Empire_Elysees** = Best Western Empire Élysées \n"
    "- **BW_Bretagne_Montparnasse** = Best Western Bretagne Montparnasse \n"
    "- **BW_Litteraire_Marcel_Ayme** = Hôtel Littéraire Marcel Aymé (BW Premier Collection) \n"
)



# --- Data loading -------------------------------------------------------------
@st.cache_data(show_spinner=False)
def load_df() -> pd.DataFrame:
    """Charge data/curated/avis_with_influence_fr.csv (essaie ';' puis ',')."""
    p = Path("data/curated/avis_with_influence_fr.csv")
    if not p.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(p, sep=";")
    except Exception:
        return pd.read_csv(p)

# --- Formatting ---------------------------------------------------------------
def format_view(df: pd.DataFrame) -> pd.DataFrame:
    """Vue lisible : colonnes clés, arrondis, aperçu texte, Oui/Non."""
    if df.empty:
        return df.copy()
    view = df.copy()

    if "avis" in view.columns:
        view["avis_apercu"] = (
            view["avis"].astype(str).str.replace("\n", " ", regex=False).str.slice(0, 180) + "…"
        )

    for col, nd in [("note", 1), ("sentiment_z", 2), ("influence_score", 2)]:
        if col in view.columns:
            view[col] = pd.to_numeric(view[col], errors="coerce").round(nd)

    if "influential_flag" in view.columns:
        view["avis_influent"] = view["influential_flag"].map({1: "Oui", 0: "Non"}).fillna("Non")

    cols_order = [
        "hotel", "auteur", "macro_topic", "note", "sentiment_z",
        "influence_score", "avis_influent", "avis_apercu"
    ]
    view = view[[c for c in cols_order if c in view.columns]]

    labels = {
        "hotel": "Hôtel",
        "auteur": "Auteur",
        "macro_topic": "Thème (catégorie)",
        "note": "Note (sur 5)",
        "sentiment_z": "Ressenti (intensité)",
        "influence_score": "Impact estimé",
        "avis_influent": "Avis influent ?",
        "avis_apercu": "Avis (aperçu)",
    }
    return view.rename(columns=labels)

# --- Intro courte -------------------------------------------------------------
st.markdown('<h3 style="color:#153E75;">Présentation</h3>', unsafe_allow_html=True)
st.markdown(
    "Cette page d’accueil offre une **vue propre et filtrable** des avis. "
    "Utilisez les filtres ci-dessous pour cibler un **hôtel**, un **thème**, "
    "ou rechercher un **mot-clé** dans le texte ou l’auteur."
)

# --- Load + Filters -----------------------------------------------------------
df = load_df()
if df.empty:
    st.warning("Place le fichier `data/curated/avis_with_influence_fr.csv` puis relance l’app.")
    st.stop()

# Filtres légers (au-dessus du tableau)
colA, colB, colC, colD = st.columns([1.1, 1.2, 1.0, 1.2])

# Hôtel
hotels = sorted(df["hotel"].dropna().unique().tolist()) if "hotel" in df.columns else []
hotel_sel = colA.selectbox("Hôtel", ["(Tous)"] + hotels) if hotels else "(Tous)"
# Thèmes
topics = sorted(df["macro_topic"].dropna().unique().tolist()) if "macro_topic" in df.columns else []
topics_sel = colB.multiselect("Thèmes", topics, default=topics)
# Influents
infl_only = colC.checkbox("Avis influents uniquement", value=False)
# Recherche
query = colD.text_input("Recherche (avis ou auteur)", "")

# Appliquer filtres
df_flt = df.copy()
if hotel_sel != "(Tous)" and "hotel" in df_flt.columns:
    df_flt = df_flt[df_flt["hotel"] == hotel_sel]
if topics_sel and "macro_topic" in df_flt.columns:
    df_flt = df_flt[df_flt["macro_topic"].isin(topics_sel)]
if infl_only and "influential_flag" in df_flt.columns:
    df_flt = df_flt[df_flt["influential_flag"] == 1]
if query:
    q = query.strip().lower()
    def _contains(s):  # petite aide pour éviter les erreurs NaN
        return s.astype(str).str.lower().str.contains(q, na=False)
    cols_q = [c for c in ["avis", "auteur"] if c in df_flt.columns]
    if cols_q:
        mask = False
        for c in cols_q:
            mask = _contains(df_flt[c]) | mask
        df_flt = df_flt[mask]

# --- Table vue propre ---------------------------------------------------------
st.subheader("Aperçu filtré")
st.caption("Colonnes principales uniquement, texte d’avis abrégé.")
st.dataframe(format_view(df_flt).head(20), use_container_width=True, hide_index=True)
