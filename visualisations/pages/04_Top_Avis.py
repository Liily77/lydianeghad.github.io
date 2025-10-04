# -*- coding: utf-8 -*-
"""
Top avis influents — version lisible pour métiers.
Cartes synthétiques + KPI + recherche/tri. Tableau + export en option.
"""

from pathlib import Path
import pandas as pd
import numpy as np
import streamlit as st

st.set_page_config(
    page_title="⭐ Top avis influents — BW Paris",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---- Habillage (sidebar + bandeau centré) -----------------------------------
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

  /* Cartes */
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
  .neg{ color:#B91C1C; } .pos{ color:#047857; } .neu{ color:#6b7280; }
  .tiny{ font-size:.86rem; }

  /* Etoiles de note */
  .star{ color:#FFD34E; }        /* jaune */
  .star-empty{ color:#E5E7EB; }  /* gris clair */
</style>
<div class="page-hero"><h1>⭐ Top avis influents</h1></div>
""", unsafe_allow_html=True)

# ---- Données -----------------------------------------------------------------
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

df = load_df()
if df.empty:
    st.warning("Place le fichier `data/curated/avis_with_influence_fr.csv` puis relance l’app.")
    st.stop()

# ---- Helpers -----------------------------------------------------------------
def sentiment_label(z: float) -> str:
    """Sens du ressenti depuis z-score (utilisé en interne, non affiché)."""
    if pd.isna(z): return "neutre"
    if z >= 0.6: return "positif"
    if z <= -0.6: return "négatif"
    return "neutre"

def intensity_label(z: float) -> str:
    """Libellé métier : positif/neutre/négatif + intensité léger/marqué/fort (sans chiffres)."""
    if pd.isna(z):
        return "neutre"
    a = abs(float(z))
    deg = "léger" if a < 0.6 else "marqué" if a < 1.5 else "fort"
    sens = sentiment_label(z)  # "positif" / "négatif" / "neutre"
    return "neutre" if sens == "neutre" else f"{sens} {deg}"

def to_note_num(s) -> float:
    """Convertit 'note' vers numérique fiable (0..5). Accepte 4,5 ou 4.5, borne 0..5."""
    x = pd.to_numeric(str(s).replace(",", "."), errors="coerce")
    if pd.isna(x): return np.nan
    return float(np.clip(x, 0.0, 5.0))

def starify(note: float) -> str:
    """HTML d'étoiles jaunes (arrondi entier)."""
    if pd.isna(note): 
        return "—"
    n = int(np.clip(np.rint(float(note)), 0, 5))
    return f"<span class='star'>{'★'*n}</span><span class='star-empty'>{'☆'*(5-n)}</span>"

def preview(txt: str, n=240) -> str:
    """Aperçu court d’un avis."""
    if not isinstance(txt, str): return ""
    s = txt.replace("\\n", " ").replace("\n", " ").strip()
    return (s[:n] + "…") if len(s) > n else s

# Colonne 'note_num' propre pour tri + affichage
if "note" in df.columns:
    df["note_num"] = df["note"].apply(to_note_num)
else:
    df["note_num"] = np.nan

# ---- Filtres lisibles --------------------------------------------------------
st.markdown('<h3 style="color:#153E75;">Filtres</h3>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns([1.1, 1.1, .9, 1.2])

hotels = sorted(df["hotel"].dropna().unique().tolist()) if "hotel" in df.columns else []
topics = sorted(df["macro_topic"].dropna().unique().tolist()) if "macro_topic" in df.columns else []

hotel_sel = c1.multiselect("Hôtel(s)", hotels, default=hotels) if hotels else []
topic_sel = c2.multiselect("Macro-thème(s)", topics, default=topics) if topics else []
only_infl = c3.toggle("Seulement influents", value=True)
search = c4.text_input("Recherche texte/auteur", value="")

tri = st.selectbox(
    "Trier par",
    ["Score influence (↓)", "Ressenti — intensité (↓)", "Note décroissante (5→0)", "Note croissante (0→5)"]
)

score_min = st.slider("Score influence minimum", 0.0, 1.0, value=0.30, step=0.05)

# Aide métier sans chiffres
st.caption("ℹ️ Ressenti = ton de l’avis (positif / neutre / négatif) + intensité (léger, marqué, fort).")

# ---- Application des filtres -------------------------------------------------
df_f = df.copy()

if hotel_sel:
    df_f = df_f[df_f["hotel"].isin(hotel_sel)]
if topic_sel:
    df_f = df_f[df_f["macro_topic"].isin(topic_sel)]
if only_infl and "influential_flag" in df_f.columns:
    df_f = df_f[df_f["influential_flag"] == 1]
if "influence_score" in df_f.columns:
    df_f = df_f[pd.to_numeric(df_f["influence_score"], errors="coerce") >= score_min]
if search:
    s = search.lower()
    df_f = df_f[
        df_f.get("avis", pd.Series("", index=df_f.index)).astype(str).str.lower().str.contains(s, na=False)
        | df_f.get("auteur", pd.Series("", index=df_f.index)).astype(str).str.lower().str.contains(s, na=False)
    ]

# Tri (intensité = |z|, mais sans afficher de chiffres)
if tri.startswith("Score"):
    df_f = df_f.sort_values("influence_score", ascending=False, na_position="last")
elif tri.startswith("Ressenti"):
    df_f = df_f.assign(_absz=np.abs(pd.to_numeric(df_f.get("sentiment_z"), errors="coerce"))) \
               .sort_values("_absz", ascending=False, na_position="last")
elif tri.startswith("Note décroissante"):
    df_f = df_f.sort_values("note_num", ascending=False, na_position="last")
elif tri.startswith("Note croissante"):
    df_f = df_f.sort_values("note_num", ascending=True, na_position="last")

# ---- KPI de contexte ---------------------------------------------------------
nb = len(df_f)
nb_infl = int(df_f["influential_flag"].sum()) if "influential_flag" in df_f.columns else nb
pct = (nb_infl / nb * 100) if nb else 0.0
note_m = df_f["note_num"].mean() if nb else np.nan

k1, k2, k3 = st.columns(3)
k1.metric("Avis affichés", f"{nb:,}".replace(",", " "))
k2.metric("% influents", f"{pct:.1f}%")
k3.metric("Note moyenne", f"{note_m:.1f}" if pd.notnull(note_m) else "–")

# ---- Mode d’affichage --------------------------------------------------------
mode = st.radio("Affichage", ["Cartes (recommandé)", "Tableau (analystes)"], horizontal=True, index=0)

# ---- Vue Cartes --------------------------------------------------------------
if mode.startswith("Cartes"):
    if nb == 0:
        st.info("Aucun avis ne correspond aux filtres.")
    else:
        max_show = min(60, max(1, nb))
        default_show = min(12, nb)
        n_show = st.slider("Nombre d’avis à montrer", 1, max_show, value=default_show)

        # Fabrique des cartes en 2 colonnes
        for i in range(0, min(n_show, nb), 2):
            cols = st.columns(2)
            for j, col in enumerate(cols):
                if i + j >= min(n_show, nb): break
                r = df_f.iloc[i+j]
                z = float(pd.to_numeric(r.get("sentiment_z", np.nan), errors="coerce"))
                lab = sentiment_label(z)
                cls = "pos" if lab=="positif" else "neg" if lab=="négatif" else "neu"
                note_num = to_note_num(r.get("note_num", r.get("note", np.nan)))
                human = intensity_label(z)
                col.markdown(f"""
                <div class="card">
                  <div class="row">
                    <span class="pill pill-hotel">{r.get('hotel','')}</span>
                    <span class="pill pill-theme">{r.get('macro_topic','')}</span>
                    {"<span class='pill pill-influent'>Influent</span>" if int(r.get("influential_flag",0))==1 else ""}
                  </div>
                  <div class="muted tiny" style="margin-top:.25rem;">
                    <b>{r.get('auteur','Anonyme')}</b>
                    {("• " + str(r.get('date'))) if 'date' in df_f.columns and pd.notnull(r.get('date')) else ""}
                  </div>
                  <h4>{starify(note_num)} <span class="muted">({note_num:.1f} / 5)</span></h4>
                  <div class="row" style="margin:.2rem 0 .35rem 0;">
                    <span class="chip score">Score influence&nbsp;: {pd.to_numeric(r.get('influence_score', np.nan), errors='coerce'):.2f}</span>
                    <span class="chip {cls}">Ressenti : {human}</span>
                    {"<span class='chip'>Score thème : {:.2f}</span>".format(pd.to_numeric(r.get('topic_score', np.nan), errors='coerce')) if 'topic_score' in df_f.columns else ""}
                  </div>
                  <div class="muted">{preview(r.get('avis',''))}</div>
                </div>
                """, unsafe_allow_html=True)

        # Export des cartes affichées
        subset = df_f.head(n_show).copy()
        if "avis" in subset.columns:
            subset["avis"] = subset["avis"].astype(str).str.replace("\n"," ", regex=False)
        st.download_button(
            "⬇️ Télécharger la sélection (CSV)",
            data=subset.to_csv(index=False).encode("utf-8-sig"),
            file_name="top_avis_selection.csv",
            mime="text/csv",
            use_container_width=True
        )

# ---- Vue Tableau -------------------------------------------------------------
else:
    def format_table(d: pd.DataFrame) -> pd.DataFrame:
        """Colonnes claires pour lecture rapide (sans chiffres de z)."""
        if d.empty: return d
        v = d.copy()
        # Texte lisible du ressenti
        v["Ressenti"] = v.get("sentiment_z").apply(intensity_label) if "sentiment_z" in v.columns else "neutre"
        if "avis" in v.columns:
            v["Avis (aperçu)"] = v["avis"].astype(str).str.replace("\n"," ", regex=False).str.slice(0, 220) + "…"
        # Arrondis sûrs (on ne montre pas z)
        for col, nd in [("note_num",1),("influence_score",2),("topic_score",2)]:
            if col in v.columns: v[col] = pd.to_numeric(v[col], errors="coerce").round(nd)
        v = v.rename(columns={
            "hotel":"Hôtel","auteur":"Auteur","macro_topic":"Macro-thème",
            "note_num":"Note","influence_score":"Score influence",
            "topic_score":"Score thème","date":"Date"
        })
        cols = [c for c in ["Hôtel","Auteur","Macro-thème","Note","Ressenti",
                            "Score influence","Score thème","Date","Avis (aperçu)"] if c in v.columns]
        return v[cols]

    if nb == 0:
        st.info("Aucun avis ne correspond aux filtres.")
    else:
        top_n = st.slider("Nombre de lignes à afficher", 20, min(300, nb), value=min(100, nb))
        table = format_table(df_f.head(top_n))
        st.dataframe(table, use_container_width=True, hide_index=True)
        st.download_button(
            "⬇️ Télécharger la sélection (CSV)",
            data=table.to_csv(index=False).encode("utf-8-sig"),
            file_name="top_avis_table.csv", mime="text/csv", use_container_width=True
        )
