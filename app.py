import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import zipfile  # Pour lire les fichiers ZIP
import os
import gdown  # Pour télécharger des fichiers depuis Google Drive
from wordcloud import WordCloud
from PIL import Image

# ---- Fonction de téléchargement depuis Google Drive ---- #
def download_data_from_drive(file_id, output_file):
    url = f"https://drive.google.com/uc?id={file_id}"
    if not os.path.exists(output_file):  # Télécharger uniquement si le fichier n'existe pas
        st.info(f"Téléchargement de {output_file} depuis Google Drive...")
        gdown.download(url, output_file, quiet=False)

# ---- Fonction de chargement des données ---- #
def load_data(file_path, file_inside_zip=None):
    try:
        # Si le fichier est compressé (ZIP)
        if file_path.endswith('.zip'):
            with zipfile.ZipFile(file_path, 'r') as z:
                with z.open(file_inside_zip) as f:
                    data = pd.read_csv(f)
        else:  # Lecture classique si non compressé
            data = pd.read_csv(file_path)
        return data
    except FileNotFoundError:
        st.error(f"Fichier introuvable : {file_path}. Vérifiez le chemin.")
        st.stop()
    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {e}")
        st.stop()

# ---- Définir les chemins et Google Drive ID ---- #
file_id = "1wBrRnTNv6dgZuHZ6fbMGicsniFhrsBok"  # ID de votre fichier Google Drive
zip_file_path = "wifi_usage_data.zip"
csv_file_inside_zip = "wifi_usage_data.csv"

# ---- Télécharger et charger les données ---- #
download_data_from_drive(file_id, zip_file_path)
wifi_usage_data = load_data(zip_file_path, csv_file_inside_zip)

# ---- Sidebar Navigation ---- #
st.sidebar.title("Navigation")
menu = st.sidebar.radio(
    "Choisissez une section :",
    [
        "Origine des données 🔎",
        "Géographique et infrastructure🌎",
        "Temporalité et comportement d'utilisation ⏲️",
        "Les utilisateurs 👩‍💻",
        "Les appareils et leurs usages 🤳🏼",
        "WorldCloud 🌎",
    ],
)

# ------------------- Section "Origine des données" ------------------------------------------- #
if menu == "Origine des données 🔎":
    # Afficher les deux images côte à côte
    col1, col2 = st.columns([1, 1])
    with col1:
        st.image("Logo1.PNG", use_container_width=True)
    with col2:
        st.image("Logo2.PNG", use_container_width=True)

    st.title("Projet Data Management 📊")
    st.markdown(
        """
        Bienvenue sur cette application Streamlit dédiée à l'analyse des données d'utilisation des hotspots Wi-Fi de Paris.

        Source des données : [Open Data](https://opendata.paris.fr/explore/dataset/paris-wi-fi-utilisation-des-hotspots-paris-wi-fi/table/).

        Objectif : Explorer les tendances d'utilisation des hotspots Wi-Fi, y compris les répartitions géographiques, temporelles, et comportementales.
        """
    )

    nombre_observations = wifi_usage_data.shape[0]
    nombre_variables = wifi_usage_data.shape[1]
    description_tableau = pd.DataFrame(
        {
            "Nom de la colonne": wifi_usage_data.columns,
            "Type de variable": wifi_usage_data.dtypes.values,
            "Nombre de valeurs": wifi_usage_data.count().values,
            "Valeurs manquantes": wifi_usage_data.isnull().sum().values,
        }
    )

    st.subheader("Description du Dataset")
    st.write("Nombre total d'observations :", nombre_observations)
    st.write("Nombre total de variables :", nombre_variables)

    st.subheader("🔎 Filtre interactif des colonnes")
    st.markdown("Utilisez le filtre pour sélectionner les colonnes que vous souhaitez afficher dans le tableau.")

    colonnes_disponibles = wifi_usage_data.columns.tolist()

    colonnes_selectionnees = st.multiselect(
        "Sélectionnez les colonnes à afficher :",
        options=colonnes_disponibles,
        default=colonnes_disponibles,
    )

    if colonnes_selectionnees:
        st.dataframe(wifi_usage_data[colonnes_selectionnees].head(10))
        st.write(f"Affichage des 10 premières lignes (sur un total de {wifi_usage_data.shape[0]} observations).")
    else:
        st.warning("Veuillez sélectionner au moins une colonne pour afficher le tableau.")

# ------------------- Section "Géographique et infrastructure" ------------------------------------------- #
elif menu == "Géographique et infrastructure🌎":
    st.title("Analyse géographique et infrastructure 🌎")
    st.markdown(
        """
        Cette section explore la répartition géographique et l'état des infrastructures Wi-Fi, permettant de visualiser l'utilisation des hotspots à travers Paris. 
        Elle inclut l'analyse des connexions par arrondissement, une carte interactive des bornes, et une évolution temporelle des états des sites Wi-Fi.
        """
    )

    tab1, tab2, tab3 = st.tabs(
        [
            "📊 Répartition par arrondissement",
            "🗺️ Carte interactive des bornes",
            "📈 Évolution des états des sites",
        ]
    )

    with tab1:
        connexions_par_arrondissement = (
            wifi_usage_data.groupby("Pénétration Géographique")["Nombre de connexions"]
            .sum()
            .reset_index()
            .rename(columns={"Nombre de connexions": "Total des connexions"})
        )
        connexions_par_arrondissement = connexions_par_arrondissement.sort_values(
            by="Total des connexions", ascending=False
        )
        fig_arrondissement = px.bar(
            connexions_par_arrondissement,
            x="Pénétration Géographique",
            y="Total des connexions",
            color="Total des connexions",
            title="Répartition des connexions Wi-Fi par arrondissement",
            color_continuous_scale="Viridis",
        )
        fig_arrondissement.update_layout(
            xaxis_title="Arrondissements",
            yaxis_title="Nombre de connexions",
            title_font=dict(size=18),
        )
        st.plotly_chart(fig_arrondissement)

    with tab2:
        wifi_usage_data[["Latitude", "Longitude"]] = wifi_usage_data[
            "geo_point_2d"
        ].str.split(",", expand=True)
        wifi_usage_data["Latitude"] = wifi_usage_data["Latitude"].astype(float)
        wifi_usage_data["Longitude"] = wifi_usage_data["Longitude"].astype(float)

        geo_data = (
            wifi_usage_data.groupby(["Latitude", "Longitude"])
            .size()
            .reset_index(name="Nombre de connexions")
        )
        fig_carte = px.scatter_mapbox(
            geo_data,
            lat="Latitude",
            lon="Longitude",
            size="Nombre de connexions",
            color="Nombre de connexions",
            color_continuous_scale=px.colors.sequential.Plasma,
            title="Carte interactive des bornes Wi-Fi avec volume de connexions",
            mapbox_style="carto-positron",
            zoom=10,
        )
        st.plotly_chart(fig_carte)

    with tab3:
        if "Date_début" in wifi_usage_data.columns:
            wifi_usage_data["Date_début"] = pd.to_datetime(
                wifi_usage_data["Date_début"], errors="coerce"
            )
            wifi_usage_data["Année"] = wifi_usage_data["Date_début"].dt.year

        etats_par_annee = (
            wifi_usage_data.groupby(["Année", "Etat du site"])
            .size()
            .reset_index(name="Nombre")
        )
        fig_etats = px.bar(
            etats_par_annee,
            x="Année",
            y="Nombre",
            color="Etat du site",
            title="Évolution des états des sites Wi-Fi par année",
            barmode="group",
            color_discrete_sequence=px.colors.qualitative.Pastel,
        )
        fig_etats.update_layout(
            xaxis_title="Année",
            yaxis_title="Nombre de sites",
            title_font=dict(size=18),
        )
        st.plotly_chart(fig_etats)

# ------------------- Section "Temporalité et comportement d'utilisation" ------------------------------------------- #
elif menu == "Temporalité et comportement d'utilisation ⏲️":
    st.title("Analyse temporelle et comportement d'utilisation ⏲️")
    st.markdown(
        """
        Cette section explore les tendances temporelles et les comportements d'utilisation des hotspots Wi-Fi.
        Elle permet de comprendre les variations annuelles, les habitudes journalières et horaires, ainsi que l'évolution mensuelle
        du temps de connexion, offrant une vue globale et détaillée des usages au fil du temps.
        """
    )

    tab1, tab2, tab3 = st.tabs([
        "📅 Fréquentations annuelles",
        "🕒 Heatmap temporelle",
        "📈 Évolution mensuelle des connexions"
    ])

    with tab1:
        st.subheader("Fréquentations annuelle des hotspots")

        wifi_usage_data["Date_début"] = pd.to_datetime(wifi_usage_data["Date_début"], errors="coerce")
        wifi_usage_data["Année"] = wifi_usage_data["Date_début"].dt.year
        df_grouped = wifi_usage_data.groupby('Année').sum(numeric_only=True)['Nombre de bornes']
        x = df_grouped.index
        y = df_grouped.values
        moyenne_connexions = y.mean()

        filtre_connexions = st.radio(
            "Filtrer les années :",
            options=["Toutes les années", "Au-dessus de la moyenne", "En dessous de la moyenne"],
            index=0
        )

        if filtre_connexions == "Au-dessus de la moyenne":
            indices = y > moyenne_connexions
        elif filtre_connexions == "En dessous de la moyenne":
            indices = y < moyenne_connexions
        else:
            indices = [True] * len(y)

        x_filtre = x[indices]
        y_filtre = y[indices]

        fig = go.Figure()

        fig.add_trace(go.Scatter(x=x_filtre, y=y_filtre, mode='lines+markers', line=dict(color='blue', width=2)))

        fig.add_trace(go.Scatter(
            x=x, 
            y=[moyenne_connexions] * len(x),
            mode='lines',
            line=dict(dash='dash', color='red'),
            name=f"Moyenne ({int(moyenne_connexions):,})"
        ))

        for xi, yi in zip(x_filtre, y_filtre):
            fig.add_annotation(
                x=xi, 
                y=yi + 20000,
                text=f"{int(yi):,}", 
                showarrow=False, 
                font=dict(size=12, color='black')
            )

        fig.update_layout(
            title="Fréquentations annuelle des hotspots",
            xaxis_title="Année",
            yaxis_title="Nombre de connexions",
            template="plotly_white",
            legend=dict(title="Légende")
        )

        st.plotly_chart(fig)

    with tab2:
        jours_attendus = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
        heatmap_data = wifi_usage_data.groupby(["Jour", "Heure"]).size().unstack(fill_value=0)
        heatmap_data = heatmap_data.reindex(jours_attendus)

        palette_couleurs = st.selectbox(
            "Choisissez une palette de couleurs pour la heatmap :",
            options=["Viridis", "Cividis", "Blues", "Hot", "Plasma", "Turbo", "YlGnBu"],
            index=0
        )

        fig_heatmap = px.imshow(
            heatmap_data,
            labels={
                "x": "Heure de la journée",
                "y": "Jour de la semaine",
                "color": "Nombre de connexions"
            },
            x=heatmap_data.columns,
            y=heatmap_data.index,
            color_continuous_scale=palette_couleurs,
            aspect="auto",
        )
        fig_heatmap.update_layout(
            xaxis_title="Heure de la journée",
            yaxis_title="Jour de la semaine",
            coloraxis_colorbar=dict(title="Nombre de connexions"),
            xaxis=dict(
                tickmode="array",
                tickvals=list(range(24)),
                ticktext=[str(i) for i in range(24)]
            )
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)

    with tab3:
        st.subheader("Temps de connexion cumulé selon le mois et l'année")

        wifi_usage_data["Année"] = wifi_usage_data["Date_début"].dt.year
        wifi_usage_data["Mois"] = wifi_usage_data["Date_début"].dt.month
        wifi_usage_data["Temps de sessions en minutes"] = pd.to_numeric(wifi_usage_data["Temps de sessions en minutes"], errors="coerce")
        temp = wifi_usage_data.groupby(['Année', 'Mois'], as_index=False)["Temps de sessions en minutes"].sum()

        min_annee, max_annee = int(wifi_usage_data['Année'].min()), int(wifi_usage_data['Année'].max())
        plage_annees = st.slider(
            "Sélectionnez une plage d'années :", 
            min_value=min_annee, 
            max_value=max_annee, 
            value=(min_annee, max_annee)
        )
        mois_selectionnes = st.multiselect(
            "Sélectionnez les mois :", 
            options=list(range(1, 13)), 
            format_func=lambda x: ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Août", "Sep", "Oct", "Nov", "Déc"][x-1],
            default=list(range(1, 13))
        )
        temp_filtre = temp[
            (temp['Année'] >= plage_annees[0]) & 
            (temp['Année'] <= plage_annees[1]) & 
            (temp['Mois'].isin(mois_selectionnes))
        ]

        if temp_filtre.empty:
            st.warning("Aucune donnée ne correspond aux critères de filtrage.")
        else:
            fig = px.line(
                temp_filtre,
                x="Mois",
                y="Temps de sessions en minutes",
                color="Année",
                markers=True,
                title="Temps de connexion cumulé selon le mois et l'année",
                labels={"Mois": "Mois", "Temps de sessions en minutes": "Total temps de session en minutes", "Année": "Année"},
                color_discrete_sequence=px.colors.qualitative.Plotly
            )
            fig.update_xaxes(
                tickmode='array',
                tickvals=list(range(1, 13)),
                ticktext=["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Août", "Sep", "Oct", "Nov", "Déc"]
            )
            fig.update_traces(line=dict(width=3), marker=dict(size=8))
            st.plotly_chart(fig, use_container_width=True)

# ------------------- Section "Les utilisateurs" ------------------------------------------- #
elif menu == "Les utilisateurs 👩‍💻":
    st.title("Analyse des utilisateurs 👥")
    st.markdown(
        """
        Ce tableau fournit une analyse des utilisateurs des hotspots Wi-Fi par langue et leur évolution au fil des années. Il permet de visualiser les langues les plus utilisées ainsi que les tendances linguistiques en fonction des années d'utilisation, offrant un aperçu des comportements des utilisateurs.
        """
    )

    tab1, tab2 = st.tabs(["Connexions par langue", "Évolution des langues par année"])

    with tab1:
        st.subheader("Nombre de connexions par langue d'utilisateur")

        corrections = {
            'Fran\x8dais': 'Français',
            'Fran‡ais': 'Français',
            'Chinois simplifi‚': 'Chinois simplifié',
            'Chinois simplifiŽ': 'Chinois simplifié',
            'CorŽen': 'Coréen',
            'Cor‚en': 'Coréen',
            'NŽerlandais': 'Néerlandais',
            'N‚erlandais': 'Néerlandais',
            'Indon‚sien': 'Indonésien'
        }
        wifi_usage_data['Langue utilisateur'] = wifi_usage_data['Langue utilisateur'].replace(corrections)

        langue_data = wifi_usage_data['Langue utilisateur'].value_counts().reset_index()
        langue_data.columns = ['Langue', 'Nombre de connexions']

        fig = px.bar(
            langue_data,
            x='Langue',
            y='Nombre de connexions',
            title="Nombre de connexions par langue d'utilisateur",
            labels={"Langue": "Langue", "Nombre de connexions": "Nombre de connexions"},
            text='Nombre de connexions'
        )
        fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
        st.plotly_chart(fig)

    with tab2:
        st.subheader("Évolution des langues des utilisateurs par année")
        wifi_usage_data["Date_début"] = pd.to_datetime(wifi_usage_data["Date_début"], errors="coerce")
        wifi_usage_data["Année"] = wifi_usage_data["Date_début"].dt.year

        evolution_data = wifi_usage_data.groupby(["Année", "Langue utilisateur"]).size().unstack(fill_value=0)
        fig = px.area(
            evolution_data,
            x=evolution_data.index,
            y=evolution_data.columns,
            title="Évolution des langues par année",
            labels={"value": "Nombre de connexions", "variable": "Langue"},
            groupnorm="fraction"
        )
        st.plotly_chart(fig)

# ------------------- Section "Les appareils et leurs usages" ------------------------------------------- #
elif menu == "Les appareils et leurs usages 🤳🏼":
    st.title("Analyse des appareils et des usages")
    st.markdown(
        """
        Cette section explore les appareils utilisés pour se connecter aux hotspots Wi-Fi et les types de données échangées.
        Elle fournit une vue sur les volumes moyens de données échangées et les répartitions des connexions par type de lieu et appareil.
        """
    )

    tab1, tab2 = st.tabs(["Volumes moyens par appareil", "Répartition par type de lieu"])

    with tab1:
        st.subheader("Volumes moyens de données échangées par appareil")
        volume_data = wifi_usage_data.groupby("Type d'appareil")[["Donnée entrante (MégaOctet)", "Donnée sortante (MégaOctet)"]].mean()

        fig, ax = plt.subplots(figsize=(10, 6))
        volume_data.plot(kind="bar", stacked=True, ax=ax, color=["#1f77b4", "#ff7f0e"])
        ax.set_title("Volumes moyens de données échangées par appareil")
        ax.set_ylabel("Volume moyen (MégaOctet)")
        ax.set_xlabel("Type d'appareil")
        st.pyplot(fig)

    with tab2:
        st.subheader("Répartition des connexions par type de lieu")
        location_data = wifi_usage_data["Lieu"].value_counts().reset_index()
        location_data.columns = ["Lieu", "Nombre de connexions"]

        fig = px.pie(
            location_data,
            values='Nombre de connexions',
            names='Lieu',
            title="Répartition des connexions par type de lieu",
            hole=0.3
        )
        st.plotly_chart(fig)

