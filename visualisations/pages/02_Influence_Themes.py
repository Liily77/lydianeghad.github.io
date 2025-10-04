# -*- coding: utf-8 -*-
"""
Influence & thèmes : heatmap hôtel × macro-thème (titres centrés, padding réduit).
"""

from pathlib import Path
import pandas as pd
import numpy as np
import streamlit as st
import altair as alt

st.set_page_config(
    page_title="🧩 Influence & thèmes — BW Paris",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Sidebar : bleu foncé + titres jaunes (style BW) --------------------------
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
    """Charge le CSV principal (essaie ';' puis ',')."""
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
<div class="page-hero"><h1>🧩 Influence & thèmes</h1></div>
""", unsafe_allow_html=True)

df = load_df()
if df.empty:
    st.warning("Place le fichier `data/curated/avis_with_influence_fr.csv` puis relance l’app.")
    st.stop()

# --- Filtres ------------------------------------------------------------------
st.markdown('<h3 style="color:#153E75;">Filtres</h3>', unsafe_allow_html=True)
hotels = sorted(df["hotel"].dropna().unique().tolist()) if "hotel" in df.columns else []
topics = sorted(df["macro_topic"].dropna().unique().tolist()) if "macro_topic" in df.columns else []

colA, colB, colC = st.columns([1.2, 1.2, 1])
hotel_sel = colA.multiselect("Hôtel(s)", hotels, default=hotels) if hotels else []
topic_sel = colB.multiselect("Macro-thème(s)", topics, default=topics) if topics else []
as_percent = colC.toggle("Afficher % d’avis influents", value=True)

df_flt = df.copy()
if hotel_sel:
    df_flt = df_flt[df_flt["hotel"].isin(hotel_sel)]
if topic_sel:
    df_flt = df_flt[df_flt["macro_topic"].isin(topic_sel)]

# --- Agrégation + Heatmap -----------------------------------------------------
if {"hotel", "macro_topic", "influential_flag"}.issubset(df_flt.columns) and len(df_flt):
    grp = (
        df_flt.assign(influential_flag=df_flt["influential_flag"].fillna(0).astype(int))
             .groupby(["hotel", "macro_topic"], dropna=False)
             .agg(
                 nb_avis=("macro_topic", "size"),
                 nb_influents=("influential_flag", "sum"),
                 note_moy=("note", "mean")
             )
             .reset_index()
    )
    grp["pct_influents"] = grp["nb_influents"] / grp["nb_avis"]

    max_nb = int(grp["nb_avis"].max()) if len(grp) else 0
    default_seuil = min(10, max_nb)
    seuil = st.slider("Seuil de volume (min. avis par cellule Hôtel × Thème)", 0, max_nb, value=default_seuil)
    grp = grp[grp["nb_avis"] >= seuil]

    if len(grp) == 0:
        st.info("Aucune cellule ne dépasse le seuil choisi.")
    else:
        value_col = "pct_influents" if as_percent else "nb_avis"
        title_val = "% influents" if as_percent else "Nb d’avis"

        ord_hotels = grp.groupby("hotel")[value_col].mean().sort_values(ascending=False).index.tolist()
        ord_topics = grp.groupby("macro_topic")[value_col].mean().sort_values(ascending=False).index.tolist()

        heat = alt.Chart(grp).mark_rect().encode(
            x=alt.X("macro_topic:N", title="Macro-thème", sort=ord_topics),
            y=alt.Y("hotel:N", title="Hôtel", sort=ord_hotels),
            color=alt.Color(f"{value_col}:Q", title=title_val,
                            scale=alt.Scale(scheme="blues")),
            tooltip=[
                alt.Tooltip("hotel:N", title="Hôtel"),
                alt.Tooltip("macro_topic:N", title="Macro-thème"),
                alt.Tooltip("nb_avis:Q", title="Nb d’avis", format=","),
                alt.Tooltip("nb_influents:Q", title="Avis influents", format=","),
                alt.Tooltip("pct_influents:Q", title="% influents", format=".1%"),
                alt.Tooltip("note_moy:Q", title="Note moyenne", format=".1f"),
            ],
        ).properties(height=420)

        labels = alt.Chart(grp).mark_text(size=11).encode(
            x=alt.X("macro_topic:N", sort=ord_topics),
            y=alt.Y("hotel:N", sort=ord_hotels),
            text=alt.Text(f"{value_col}:Q", format=".0%" if as_percent else ","),
            color=alt.value("#0F2F57")
        )

        st.altair_chart(heat + labels, use_container_width=True)
        st.caption(
            "Chaque case = (Hôtel, Macro-thème). Valeur : **% d’avis influents** (ou **Nb d’avis**). "
            "Utilisez le **seuil** pour ignorer les cellules peu représentées."
        )
else:
    st.info("Colonnes manquantes : hotel / macro_topic / influential_flag.")

