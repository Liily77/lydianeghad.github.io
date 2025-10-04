# -*- coding: utf-8 -*-
"""
ℹ️ Aide & Méthodo — BW Paris
Glossaire (sans maths) + comment lire les pages + qualité des données + mini graphiques.
"""

from pathlib import Path
import pandas as pd
import numpy as np
import streamlit as st
import altair as alt

st.set_page_config(
    page_title="ℹ️ Aide & Méthodo — BW Paris",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---- Habillage (même design BW) ---------------------------------------------
st.markdown("""
<style>
  [data-testid="stSidebar"]{
    background: linear-gradient(180deg,#0F2F57 0%, #153E75 55%, #1C4F8C 100%) !important;
    border-right: 1px solid rgba(0,0,0,.15);
  }
  [data-testid="stSidebar"] *, [data-testid="stSidebar"] a{ color:#FFD34E !important; text-decoration:none!important; }
  .page-hero{ background:linear-gradient(90deg,#153E75 0%,#1C4F8C 45%,#0F2F57 100%);
              color:#fff; padding:10px 14px; border-radius:12px; margin-bottom:10px; text-align:center; }
  .page-hero h1{ margin:0; font-size:1.15rem; }

  .card{ border:1px solid #e6e2d8; background:#fff; border-radius:14px; padding:12px 14px; margin-bottom:10px; }
  .card h4{ margin:.25rem 0; color:#153E75; }
  .muted{ color:#6b7280; font-size:.92rem; }
  .row{ display:flex; gap:10px; flex-wrap:wrap; }
  .pill{ display:inline-block; padding:.15rem .5rem; border-radius:999px; font-size:.85rem; margin-right:.35rem; }
  .pill-hotel{ background:#EFF6FF; color:#153E75; border:1px solid #DAE6FF; }
  .pill-theme{ background:#F5F3FF; color:#3730A3; border:1px solid #E5E7EB; }
  .pill-influent{ background:#FFF7ED; color:#B45309; border:1px solid #FDE68A; }
  .chip{ background:#F3F4F6; border:1px solid #E5E7EB; padding:.15rem .45rem; border-radius:8px; font-size:.85rem; }
  .score{ font-weight:600; color:#0F2F57; }
  .tiny{ font-size:.86rem; }

  /* Etoiles jaunes si besoin d’exemples */
  .star{ color:#FFD34E; } .star-empty{ color:#E5E7EB; }
</style>
<div class="page-hero"><h1>ℹ️ Aide & Méthodo</h1></div>
""", unsafe_allow_html=True)

# ---- Chargement données ------------------------------------------------------
@st.cache_data(show_spinner=False)
def load_df() -> pd.DataFrame:
    p = Path("data/curated/avis_with_influence_fr.csv")
    if not p.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(p, sep=";")
    except Exception:
        return pd.read_csv(p)

df = load_df()
if df.empty:
    st.warning("Place le fichier `data/curated/avis_with_influence_fr.csv` puis relance l’app.")
    st.stop()

# ---- Helpers -----------------------------------------------------------------
def to_num(x): return pd.to_numeric(x, errors="coerce")
def to_note_num(x):
    x = pd.to_numeric(str(x).replace(",", "."), errors="coerce")
    return float(np.clip(x, 0, 5)) if pd.notnull(x) else np.nan

# Colonnes harmonisées (sans casser si absentes)
df["hotel"] = df.get("hotel", "")
df["auteur"] = df.get("auteur", "Anonyme").fillna("Anonyme").replace({"": "Anonyme"})
df["note_num"] = df.get("note", np.nan).apply(to_note_num) if "note" in df.columns else np.nan
df["influential_flag"] = to_num(df.get("influential_flag"))
df["influence_score"] = to_num(df.get("influence_score"))
dates = pd.to_datetime(df.get("date"), errors="coerce") if "date" in df.columns else pd.Series(pd.NaT, index=df.index)

# ---- Résumé qualité / couverture --------------------------------------------
nb = len(df)
nb_hotels = df["hotel"].nunique() if "hotel" in df.columns else 0
pct_infl = (df["influential_flag"].fillna(0).sum()/nb*100) if nb else 0
note_m = df["note_num"].mean() if nb else np.nan
date_min = pd.to_datetime(dates.min()).date() if dates.notna().any() else None
date_max = pd.to_datetime(dates.max()).date() if dates.notna().any() else None
pct_auth_missing = (df["auteur"].eq("Anonyme").mean()*100) if "auteur" in df.columns else np.nan

k1, k2, k3, k4 = st.columns(4)
k1.metric("Avis (curated)", f"{nb:,}".replace(",", " "))
k2.metric("Hôtels couverts", f"{nb_hotels}")
k3.metric("% d’avis influents", f"{pct_infl:.1f}%")
k4.metric("Note moyenne", f"{note_m:.1f}" if pd.notnull(note_m) else "–")
st.caption(f"Période couverte : {date_min} → {date_max}" if date_min and date_max else "Période non disponible")
st.caption(f"% d’auteurs anonymes/alias : {pct_auth_missing:.1f}%" if pd.notnull(pct_auth_missing) else "")

# ---- Comment lire l’application (sans maths) ---------------------------------
st.markdown("""
### Comment lire les pages
- **Supervision** : vue d’ensemble. Regardez surtout le **% d’avis influents par hôtel** : là où c’est haut, le **risque d’image** est plus fort.
- **Influence & thèmes** : la **heatmap Hôtel × Macro-thème** montre **où** ça coince (volume ou % d’influents). Filtrez par hôtel/thème pour cadrer.
- **Priorités (par hôtel)** : pour un hôtel, la **priorité = volume × % d’influents**. Traitez d’abord le **Top 3** proposé.
- **Top avis** : exemples concrets pour **briefer les équipes** (tags thème, ⭐ note, ressenti texte, score d’influence).
""")

with st.expander("Glossaire (vulgarisé)", expanded=True):
    st.markdown("""
- **Avis influent** : avis long/structuré + ressenti marqué + thème clair → il **pèse** plus dans la perception.
- **Ressenti (z)** : étiquette simple du ton (**positif / neutre / négatif**) calculée par le modèle ; pas besoin de chiffres ici.
- **Macro-thème** : regroupement de sujets (ex. *Chambres*, *Petit-déj*, *Accueil*…) pour agir vite au bon endroit.
- **Priorité** : mélange **quantité + intensité** (beaucoup d’avis **et** souvent influents) ⇒ à traiter **en premier**.
- **Score d’influence** (avis) : indicateur 0–1. Plus c’est haut, plus l’avis est structuré, chargé en ressenti, et **lisible** par d’autres.
""")

with st.expander("Limites & bonnes pratiques", expanded=False):
    st.markdown("""
- **Auteurs génériques** (“Trip member”…): peu actionnables → utilisez-les pour les thèmes, pas pour du CRM.
- **Bruit de collecte** : doublons possibles, langues mixtes, dates manquantes ; lisez **Top avis** pour valider.
- **Modèle** : le but est de **prioriser** (ordre de traitement), pas de donner des chiffres “absolus”.
""")

# ---- Qualité par hôtel -------------------------------------------------------
st.markdown("### Qualité & couverture par hôtel")
if "hotel" in df.columns and nb:
    grp = (df.groupby("hotel", dropna=False)
             .agg(Nb_avis=("hotel","size"),
                  Pct_influents=("influential_flag", lambda s: (pd.to_numeric(s, errors="coerce").fillna(0).mean()*100)),
                  Note_moy=("note_num","mean"))
             .reset_index())
    for col, nd in [("Pct_influents",1), ("Note_moy",1)]:
        if col in grp.columns: grp[col] = pd.to_numeric(grp[col], errors="coerce").round(nd)
    st.dataframe(grp.rename(columns={"hotel":"Hôtel","Nb_avis":"Nb d’avis","Pct_influents":"% influents","Note_moy":"Note moy."}),
                 use_container_width=True, hide_index=True)
else:
    st.caption("Colonnes hôtel/avis non disponibles.")

# ---- Mini-graphes (optionnels) ----------------------------------------------
c1, c2 = st.columns(2)

with c1:
    st.markdown("**Volume par mois**")
    if dates.notna().any():
        d2 = pd.DataFrame({"mois": dates.dt.to_period("M").dt.to_timestamp(), "n": 1}).groupby("mois").sum().reset_index()
        chart = alt.Chart(d2).mark_bar().encode(
            x=alt.X("mois:T", title="Mois"),
            y=alt.Y("n:Q", title="Nb d’avis"),
            tooltip=[alt.Tooltip("mois:T", title="Mois"), alt.Tooltip("n:Q", title="Avis")]
        ).properties(height=220)
        st.altair_chart(chart, use_container_width=True)
    else:
        st.caption("Pas de dates pour tracer le volume.")

with c2:
    st.markdown("**Distribution des notes**")
    if "note_num" in df.columns and df["note_num"].notna().any():
        chart2 = alt.Chart(df.dropna(subset=["note_num"])).mark_bar().encode(
            x=alt.X("note_num:Q", bin=alt.Bin(step=0.5), title="Note (bin 0.5)"),
            y=alt.Y("count():Q", title="Nb d’avis"),
            tooltip=[alt.Tooltip("count():Q", title="Avis")]
        ).properties(height=220)
        st.altair_chart(chart2, use_container_width=True)
    else:
        st.caption("Pas de notes disponibles.")

# ---- Exports “mémoire” (sélection simple) -----------------------------------
st.markdown("### Exports rapides")
cols = ["hotel","auteur","macro_topic","note","influence_score","influential_flag","date","avis"]
export_cols = [c for c in cols if c in df.columns]
if export_cols:
    df_out = df[export_cols].copy()
    # aplatir lignes longues pour export
    if "avis" in df_out.columns:
        df_out["avis"] = df_out["avis"].astype(str).str.replace("\n", " ", regex=False)
    st.download_button(
        "⬇️ Export CSV (colonnes clés)",
        data=df_out.to_csv(index=False).encode("utf-8-sig"),
        file_name="export_bw_paris_colonnes_cles.csv",
        mime="text/csv",
        use_container_width=True
    )
else:
    st.caption("Colonnes clés non trouvées pour l’export.")
