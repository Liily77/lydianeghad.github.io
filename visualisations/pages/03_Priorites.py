# -*- coding: utf-8 -*-
"""
Priorités : par hôtel, repérer les macro-thèmes à traiter en premier.
Bulle = thème ; X = % influents ; Y = note moyenne ; Taille = priorité.
"""

from pathlib import Path
import pandas as pd
import numpy as np
import streamlit as st
import altair as alt

st.set_page_config(
    page_title="🎯 Priorités — BW Paris",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Sidebar bleu BW + textes jaunes -----------------------------------------
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

# --- Données ------------------------------------------------------------------
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

# --- En-tête (centré, padding réduit) ----------------------------------------
st.markdown("""
<style>
  .page-hero{
    background: linear-gradient(90deg, #153E75 0%, #1C4F8C 45%, #0F2F57 100%);
    color: #fff; padding: 10px 14px; border-radius: 12px; margin-bottom: 10px;
    text-align: center;
  }
  .page-hero h1{ margin: 0; font-size: 1.15rem; }
</style>
<div class="page-hero"><h1>🎯 Priorités d’action par hôtel</h1></div>
""", unsafe_allow_html=True)

df = load_df()
if df.empty:
    st.warning("Place le fichier `data/curated/avis_with_influence_fr.csv` puis relance l’app.")
    st.stop()

# --- Filtres ------------------------------------------------------------------
st.markdown('<h3 style="color:#153E75;">Filtres</h3>', unsafe_allow_html=True)
hotels = sorted(df["hotel"].dropna().unique().tolist()) if "hotel" in df.columns else []
hotel = st.selectbox("Hôtel", hotels, index=0 if hotels else None)
seuil_nb = st.slider("Seuil de volume (min. avis par thème)", 0, 50, value=10)

# --- Agrégations --------------------------------------------------------------
d = df[df["hotel"] == hotel].copy() if hotel else df.copy()
if {"macro_topic", "influential_flag"}.issubset(d.columns) and len(d):

    # Vue thèmes pour l’hôtel sélectionné
    g = (
        d.assign(influential_flag=d["influential_flag"].fillna(0).astype(int))
         .groupby("macro_topic", dropna=False)
         .agg(nb_avis=("macro_topic", "size"),
              nb_influents=("influential_flag", "sum"),
              note_moy=("note", "mean"))
         .reset_index()
    )
    g = g[g["nb_avis"] >= seuil_nb]
    if len(g) == 0:
        st.info("Aucun thème ne dépasse le seuil choisi.")
        st.stop()

    # % influents et priorité (= Nb d’avis × % influents == nb_influents)
    g["pct_influents"] = g["nb_influents"] / g["nb_avis"]
    g["priorite"] = g["nb_avis"] * g["pct_influents"]

    # --- KPI rapides pour l’hôtel -------------------------------------------
    c1, c2, c3 = st.columns(3)
    tot, infl = int(g["nb_avis"].sum()), int(g["nb_influents"].sum())
    pct = (infl / tot * 100) if tot else 0
    note = d["note"].mean() if "note" in d.columns else np.nan
    c1.metric("Nb d’avis (somme thèmes gardés)", f"{tot:,}".replace(",", " "))
    c2.metric("Avis influents (≈ priorité totale)", f"{infl:,}".replace(",", " "))
    c3.metric("Note moyenne", f"{note:.1f}" if pd.notnull(note) else "–")

        # --- Classement des thèmes (barres horizontales) -----------------------------
    st.markdown('<h3 style="color:#153E75; text-align:center;">Classement des thèmes — priorité</h3>',
                unsafe_allow_html=True)

    colL, colM = st.columns([1, 1])
    top_n = colL.slider("Nombre de thèmes à afficher", 3, len(g), value=min(8, len(g)))
    color_by_pct = colM.checkbox("Colorer par % d’influents", value=True)

    # Tri + sélection
    g2 = g.sort_values("priorite", ascending=False).head(top_n).copy()
    # Libellé compact à afficher en bout de barre
    g2["lbl"] = (g2["pct_influents"]*100).round(1).astype(str) + "%  •  note " + g2["note_moy"].round(1).astype(str)

    base = alt.Chart(g2).properties(height=max(260, 32*len(g2)+40))

    bars = base.mark_bar().encode(
        x=alt.X("priorite:Q", title="Priorité (≈ nombre d’avis influents)"),
        y=alt.Y("macro_topic:N", sort="-x", title="Macro-thème"),
        color=(
            alt.Color("pct_influents:Q", title="% influents",
                    scale=alt.Scale(scheme="blues")) if color_by_pct
            else alt.value("#153E75")
        ),
        tooltip=[
            alt.Tooltip("macro_topic:N", title="Macro-thème"),
            alt.Tooltip("nb_avis:Q", title="Nb d’avis", format=","),
            alt.Tooltip("nb_influents:Q", title="Avis influents", format=","),
            alt.Tooltip("pct_influents:Q", title="% influents", format=".1%"),
            alt.Tooltip("note_moy:Q", title="Note moyenne", format=".1f"),
            alt.Tooltip("priorite:Q", title="Priorité", format=".2f"),
        ],
    )

    labels = base.mark_text(align="left", dx=6, color="#0F2F57", fontSize=12).encode(
        x="priorite:Q",
        y=alt.Y("macro_topic:N", sort="-x"),
        text="lbl:N",
    )

    st.altair_chart(bars + labels, use_container_width=True)




    # --- Top 3 recommandations ----------------------------------------------
    st.markdown("**Top 3 thèmes à traiter en premier (par priorité)**")
    top3 = g.sort_values("priorite", ascending=False).head(3)
    for _, r in top3.iterrows():
        st.markdown(
            f"- **{r['macro_topic']}** — priorité **{r['priorite']:.2f}** "
            f"(Nb: {int(r['nb_avis'])}, % infl.: {r['pct_influents']*100:.1f}%, note: {r['note_moy']:.1f})"
        )

    # --- Tableau + export ----------------------------------------------------
    st.markdown('<h4 style="color:#153E75; text-align:center;">Détail par thème (filtrable & export)</h4>',
                unsafe_allow_html=True)
    tab = g.copy()
    tab["% influents"] = (tab["pct_influents"] * 100).round(1)
    tab["Note moyenne"] = tab["note_moy"].round(1)
    tab = tab.rename(columns={
        "macro_topic": "Macro-thème",
        "nb_avis": "Nb d’avis",
        "nb_influents": "Avis influents",
        "priorite": "Priorité"
    })[["Macro-thème", "Nb d’avis", "Avis influents", "% influents", "Note moyenne", "Priorité"]]
    st.dataframe(tab.sort_values("Priorité", ascending=False), use_container_width=True, hide_index=True)

    st.download_button(
        "⬇️ Télécharger (priorités par thème, CSV)",
        data=tab.to_csv(index=False).encode("utf-8-sig"),
        file_name=f"priorites_{hotel}.csv",
        mime="text/csv",
        use_container_width=True
    )

else:
    st.info("Colonnes manquantes : hotel / macro_topic / influential_flag.")
