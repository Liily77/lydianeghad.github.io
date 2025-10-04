# -*- coding: utf-8 -*-
"""
Supervision : sidebar bleue + filtre hôtels + 4 KPI + 2 graphiques (titres centrés, padding réduit).
"""

from pathlib import Path
import pandas as pd
import numpy as np
import streamlit as st
import altair as alt  # graphiques

st.set_page_config(
    page_title="📊 Supervision — BW Paris",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Sidebar : bleu foncé + titres jaunes ------------------------------------
st.markdown("""
<style>
  [data-testid="stSidebar"]{
    background: linear-gradient(180deg,#0F2F57 0%, #153E75 55%, #1C4F8C 100%) !important;
    border-right: 1px solid rgba(0,0,0,.15);
  }
  [data-testid="stSidebar"] *, [data-testid="stSidebar"] a{
    color: #FFD34E !important; text-decoration: none !important;
  }
  [data-testid="stSidebar"] svg{ fill: #FFD34E !important; }
</style>
""", unsafe_allow_html=True)

# --- Chargement ---------------------------------------------------------------
@st.cache_data(show_spinner=False)
def load_df() -> pd.DataFrame:
    """Lit le CSV principal (essaie ';' puis ',')."""
    p = Path("data/curated/avis_with_influence_fr.csv")
    if not p.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(p, sep=";")
    except Exception:
        return pd.read_csv(p)

# --- En-tête (centré + padding réduit) ---------------------------------------
st.markdown("""
<style>
  .page-hero{
    background: linear-gradient(90deg, #153E75 0%, #1C4F8C 45%, #0F2F57 100%);
    color: #fff; padding: 10px 14px; border-radius: 12px; margin-bottom: 10px;
    text-align: center;
  }
  .page-hero h1{ margin: 0; font-size: 1.15rem; }
</style>
<div class="page-hero"><h1>📊 Supervision</h1></div>
""", unsafe_allow_html=True)

df = load_df()
if df.empty:
    st.warning("Place le fichier `data/curated/avis_with_influence_fr.csv` puis relance l’app.")
    st.stop()

# --- Filtres ------------------------------------------------------------------
st.markdown('<h3 style="color:#153E75;">Filtres</h3>', unsafe_allow_html=True)
hotels = sorted(df["hotel"].dropna().unique().tolist()) if "hotel" in df.columns else []
hotel_sel = st.multiselect("Hôtel(s)", hotels, default=hotels) if hotels else []
df_flt = df[df["hotel"].isin(hotel_sel)] if hotel_sel else df.copy()

# --- KPI ----------------------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)
nb = len(df_flt)
nb_infl = int(df_flt["influential_flag"].sum()) if "influential_flag" in df_flt.columns else 0
pct = (nb_infl / nb) * 100 if nb else 0.0
note_m = df_flt["note"].mean() if "note" in df_flt.columns and nb else np.nan

with c1: st.metric("Nb d'avis", f"{nb:,}".replace(",", " "))
with c2: st.metric("Avis influents", f"{nb_infl:,}".replace(",", " "))
with c3: st.metric("% influents", f"{pct:.1f}%")
with c4: st.metric("Note moyenne", f"{note_m:.1f}" if pd.notnull(note_m) else "–")

st.caption("Vue d’ensemble avant le détail par hôtel et par thème.")

# --- Graphe 1 : % d'avis influents par hôtel ---------------------------------
st.markdown('<h3 style="color:#153E75;">% d’avis influents par hôtel</h3>', unsafe_allow_html=True)

if {"hotel", "influential_flag"}.issubset(df_flt.columns):
    agg = (
        df_flt.assign(influential_flag=df_flt["influential_flag"].fillna(0).astype(int))
              .groupby("hotel", dropna=False)
              .agg(
                  nb_avis=("hotel", "size"),
                  nb_influents=("influential_flag", "sum"),
                  note_moy=("note", "mean"),
              )
              .reset_index()
    )
    agg["pct_influents"] = agg["nb_influents"] / agg["nb_avis"]
    agg = agg.sort_values("pct_influents", ascending=False)

    base = alt.Chart(agg).properties(height=300)
    bars = base.mark_bar(color="#153E75").encode(
        x=alt.X("pct_influents:Q", title="% influents", axis=alt.Axis(format="%")),
        y=alt.Y("hotel:N", sort="-x", title="Hôtel"),
        tooltip=[
            alt.Tooltip("hotel:N", title="Hôtel"),
            alt.Tooltip("nb_avis:Q", title="Nb d'avis", format=","),
            alt.Tooltip("nb_influents:Q", title="Avis influents", format=","),
            alt.Tooltip("pct_influents:Q", title="% influents", format=".1%"),
            alt.Tooltip("note_moy:Q", title="Note moyenne", format=".1f"),
        ],
    )
    labels = base.mark_text(align="left", dx=4, color="#0F2F57").encode(
        y=alt.Y("hotel:N", sort="-x"),
        x=alt.X("pct_influents:Q"),
        text=alt.Text("pct_influents:Q", format=".1%")
    )
    st.altair_chart(bars + labels, use_container_width=True)
    st.caption("Calcul : nb d’avis influents / nb d’avis (par hôtel). Tri décroissant.")
else:
    st.info("Colonnes manquantes pour ce graphe (hotel / influential_flag).")

# --- Graphe 2 : Macro-thèmes les plus “influents” -----------------------------
st.markdown('<h3 style="color:#153E75;">Macro-thèmes les plus “influents”</h3>', unsafe_allow_html=True)

if {"macro_topic", "influential_flag"}.issubset(df_flt.columns):
    agg_t = (
        df_flt.assign(influential_flag=df_flt["influential_flag"].fillna(0).astype(int))
              .groupby("macro_topic", dropna=False)
              .agg(
                  nb_avis=("macro_topic", "size"),
                  nb_influents=("influential_flag", "sum"),
                  note_moy=("note", "mean"),
              )
              .reset_index()
    )
    agg_t["pct_influents"] = agg_t["nb_influents"] / agg_t["nb_avis"]

    max_nb = int(agg_t["nb_avis"].max()) if len(agg_t) else 0
    default_seuil = min(20, max_nb)
    seuil = st.slider("Seuil de volume (min. avis par thème)", 0, max_nb, value=default_seuil)

    agg_t = agg_t[agg_t["nb_avis"] >= seuil].sort_values("pct_influents", ascending=False).head(10)

    base2 = alt.Chart(agg_t).properties(height=300)
    bars2 = base2.mark_bar(color="#1C4F8C").encode(
        x=alt.X("pct_influents:Q", title="% influents", axis=alt.Axis(format="%")),
        y=alt.Y("macro_topic:N", sort="-x", title="Macro-thème"),
        tooltip=[
            alt.Tooltip("macro_topic:N", title="Macro-thème"),
            alt.Tooltip("nb_avis:Q", title="Nb d'avis", format=","),
            alt.Tooltip("nb_influents:Q", title="Avis influents", format=","),
            alt.Tooltip("pct_influents:Q", title="% influents", format=".1%"),
            alt.Tooltip("note_moy:Q", title="Note moyenne", format=".1f"),
        ],
    )
    labels2 = base2.mark_text(align="left", dx=4, color="#0F2F57").encode(
        y=alt.Y("macro_topic:N", sort="-x"),
        x=alt.X("pct_influents:Q"),
        text=alt.Text("pct_influents:Q", format=".1%")
    )
    st.altair_chart(bars2 + labels2, use_container_width=True)
    st.caption("Top 10 par % d’avis influents (après filtrage par volume).")
else:
    st.info("Colonnes manquantes pour ce graphe (macro_topic / influential_flag).")
