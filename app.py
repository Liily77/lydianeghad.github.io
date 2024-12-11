import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import zipfile  # Ajouté pour lire les fichiers ZIP


# ---- Lecture des données ---- #
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

# Nom du fichier compressé et du fichier CSV à l'intérieur
file_path = "wifi_usage_data.zip"
file_inside_zip = "wifi_usage_data.csv"

# Charger les données
wifi_usage_data = load_data(file_path, file_inside_zip)


# ---- Sidebar Navigation ---- #

st.sidebar.title("Navigation")
menu = st.sidebar.radio("Choisissez une section :", ["Origine des données 🔎", "Géographique et infrastructure🌎", "Temporalité et comportement d'utilisation ⏲️", "Les utilisateurs 👩‍💻", "Les appareils et leurs usages 🤳🏼","WorldCloud 🌎"])

# ------------------- Section "Origine des données" ------------------------------------------- #

if menu == "Origine des données 🔎":

    # Afficher les deux images côte à côte
    col1, col2 = st.columns([1, 1])  # Crée deux colonnes de largeur égale

    with col1:
        st.image("Logo1.PNG", use_container_width=True)  # Charger la première image

    with col2:
        st.image("Logo2.PNG", use_container_width=True)  # Charger la seconde image

    st.title("Projet Data Management 📊")
    st.markdown("""
    Bienvenue sur cette application Streamlit dédiée à l'analyse des données d'utilisation des hotspots Wi-Fi de Paris.
                
    Source des données : [Open Data](https://opendata.paris.fr/explore/dataset/paris-wi-fi-utilisation-des-hotspots-paris-wi-fi/table/?disjunctive.incomingzonelabel&disjunctive.incomingnetworklabel&disjunctive.device_portal_format&disjunctive.device_constructor_name&disjunctive.device_operating_system_name_version&disjunctive.device_browser_name_version&disjunctive.userlanguage).

    Objectif : Explorer les tendances d'utilisation des hotspots Wi-Fi, y compris les répartitions géographiques, temporelles, et comportementales.
    """)

    # ---- Création d'un tableau récapitulatif ---- #

    nombre_observations = wifi_usage_data.shape[0]
    nombre_variables = wifi_usage_data.shape[1]

    description_tableau = pd.DataFrame({
        "Nom de la colonne": wifi_usage_data.columns,
        "Type de variable": wifi_usage_data.dtypes.values,
        "Nombre de valeurs": wifi_usage_data.count().values,
        "Valeurs manquantes": wifi_usage_data.isnull().sum().values
    })

    st.subheader("Description du Dataset")
    st.write("Nombre total d'observations :", nombre_observations)
    st.write("Nombre total de variables :", nombre_variables)
    

    # ---- Tableau récapitulatif avec filtre ---- #

    st.subheader("🔎 Filtre interactif des colonnes")
    st.markdown("Utilisez le filtre pour sélectionner les colonnes que vous souhaitez afficher dans le tableau.")

  
    colonnes_disponibles = wifi_usage_data.columns.tolist()

    # --- Widget multiselect pour choisir les colonnes

    colonnes_selectionnees = st.multiselect(
        "Sélectionnez les colonnes à afficher :",
        options=colonnes_disponibles,
        default=colonnes_disponibles  # Par défaut, toutes les colonnes sont affichées
    )

    #---- Affichage du tableau filtré
    if colonnes_selectionnees:
        st.dataframe(wifi_usage_data[colonnes_selectionnees])
    else:
        st.warning("Veuillez sélectionner au moins une colonne pour afficher le tableau.")
    

# ------------------- Section "Géographique et infrastructure" ------------------------------------------- #

elif menu == "Géographique et infrastructure🌎":
    st.title("Analyse géographique et infrastructure 🌎")
    st.markdown("""
    Cette section explore la répartition géographique et l'état des infrastructures Wi-Fi, permettant de visualiser l'utilisation des hotspots à travers Paris. 
    Elle inclut l'analyse des connexions par arrondissement, une carte interactive des bornes, et une évolution temporelle des états des sites Wi-Fi.
    """)

    # ---- Création des onglets ---- #
    tab1, tab2, tab3 = st.tabs(["📊 Répartition par arrondissement", "🗺️ Carte interactive des bornes", "📈 Évolution des états des sites"])

    # ---- Graphique 1 : Répartition des connexions par arrondissement ---- #
    
    with tab1:

        connexions_par_arrondissement = (   
            wifi_usage_data.groupby("Pénétration Géographique")["Nombre de connexions"]
            .sum()
            .reset_index()
            .rename(columns={"Nombre de connexions": "Total des connexions"})
        )
        connexions_par_arrondissement = connexions_par_arrondissement.sort_values(by="Total des connexions", ascending=False)
        fig_arrondissement = px.bar(
            connexions_par_arrondissement,
            x="Pénétration Géographique",
            y="Total des connexions",
            color="Total des connexions",
            title="Répartition des connexions Wi-Fi par arrondissement",
            color_continuous_scale="Viridis"
        )
        fig_arrondissement.update_layout(xaxis_title="Arrondissements", yaxis_title="Nombre de connexions", title_font=dict(size=18))
        st.plotly_chart(fig_arrondissement)

    # ---- Graphique 2 : Carte interactive des bornes Wi-Fi ---- #

    with tab2:

        # Séparer latitude et longitude
        wifi_usage_data[["Latitude", "Longitude"]] = wifi_usage_data["geo_point_2d"].str.split(',', expand=True)
        wifi_usage_data["Latitude"] = wifi_usage_data["Latitude"].astype(float)
        wifi_usage_data["Longitude"] = wifi_usage_data["Longitude"].astype(float)

        # Groupement des données par latitude et longitude
        geo_data = wifi_usage_data.groupby(["Latitude", "Longitude"]).size().reset_index(name="Nombre de connexions")

        # Création du graphique
        fig_carte = px.scatter_mapbox(
            geo_data,
            lat="Latitude",
            lon="Longitude",
            size="Nombre de connexions",
            color="Nombre de connexions",
            color_continuous_scale=px.colors.sequential.Plasma,
            title="Carte interactive des bornes Wi-Fi avec volume de connexions",
            mapbox_style="carto-positron",
            zoom=10
        )
        st.plotly_chart(fig_carte)

    # ---- Graphique 3 : Évolution des états des sites Wi-Fi ---- #

    with tab3:
        
        # Conversion et extraction de l'année
        if "Date_début" in wifi_usage_data.columns:
            wifi_usage_data["Date_début"] = pd.to_datetime(wifi_usage_data["Date_début"], errors="coerce")
            wifi_usage_data["Année"] = wifi_usage_data["Date_début"].dt.year

        # Groupement des données par année et état des sites
        etats_par_annee = wifi_usage_data.groupby(["Année", "Etat du site"]).size().reset_index(name="Nombre")

        # Création du graphique
        fig_etats = px.bar(
            etats_par_annee,
            x="Année",
            y="Nombre",
            color="Etat du site",
            title="Évolution des états des sites Wi-Fi par année",
            barmode="group",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_etats.update_layout(xaxis_title="Année", yaxis_title="Nombre de sites", title_font=dict(size=18))
        st.plotly_chart(fig_etats)

# ------------------- Section "Temporalité et comportement d'utilisation" ------------------------------------------- #

elif menu == "Temporalité et comportement d'utilisation ⏲️":
    st.title("Analyse temporelle et comportement d'utilisation ⏲️")
    st.markdown("""
    Cette section explore les tendances temporelles et les comportements d'utilisation des hotspots Wi-Fi.
    Elle permet de comprendre les variations annuelles, les habitudes journalières et horaires, ainsi que l'évolution mensuelle
    du temps de connexion, offrant une vue globale et détaillée des usages au fil du temps.
    """)

    # ---- Création des onglets ---- #
    tab1, tab2, tab3 = st.tabs([
        "📅 Fréquentations annuelles",
        "🕒 Heatmap temporelle",
        "📈 Évolution mensuelle des connexions"
    ])

    # ---- Graphique 1 : Fréquentation annuelle des hotspots ---- #
    with tab1:
        st.subheader("Fréquentations annuelle des hotspots")

        # Extraction et regroupement des données
        wifi_usage_data["Date_début"] = pd.to_datetime(wifi_usage_data["Date_début"], errors="coerce")
        wifi_usage_data["Année"] = wifi_usage_data["Date_début"].dt.year
        df_grouped = wifi_usage_data.groupby('Année').sum(numeric_only=True)['Nombre de bornes']
        x = df_grouped.index
        y = df_grouped.values
        moyenne_connexions = y.mean()  # Calcul de la moyenne

        # Options interactives
        filtre_connexions = st.radio(
            "Filtrer les années :",
            options=["Toutes les années", "Au-dessus de la moyenne", "En dessous de la moyenne"],
            index=0
        )

        # Application du filtre
        if filtre_connexions == "Au-dessus de la moyenne":
            indices = y > moyenne_connexions
        elif filtre_connexions == "En dessous de la moyenne":
            indices = y < moyenne_connexions
        else:
            indices = [True] * len(y)  # Toutes les années

        x_filtre = x[indices]
        y_filtre = y[indices]

        # Création du graphique avec Plotly
        fig = go.Figure()

        # Ligne des données filtrées
        fig.add_trace(go.Scatter(x=x_filtre, y=y_filtre, mode='lines+markers', line=dict(color='blue', width=2)))

        # Ligne horizontale pour la moyenne
        fig.add_trace(go.Scatter(
            x=x, 
            y=[moyenne_connexions] * len(x),
            mode='lines',
            line=dict(dash='dash', color='red'),
            name=f"Moyenne ({int(moyenne_connexions):,})"
        ))

        # Ajout des annotations
        for xi, yi in zip(x_filtre, y_filtre):
            fig.add_annotation(
                x=xi, 
                y=yi + 20000,  # Décalage pour éviter le chevauchement
                text=f"{int(yi):,}", 
                showarrow=False, 
                font=dict(size=12, color='black')
            )

        # Mise en forme du graphique
        fig.update_layout(
            title="Fréquentations annuelle des hotspots",
            xaxis_title="Année",
            yaxis_title="Nombre de connexions",
            template="plotly_white",
            legend=dict(title="Légende")
        )

        st.plotly_chart(fig)

    # ---- Graphique 2 : Heatmap temporelle ---- #
    with tab2:
        # Préparation des données pour la heatmap
        jours_attendus = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
        heatmap_data = wifi_usage_data.groupby(["Jour", "Heure"]).size().unstack(fill_value=0)
        heatmap_data = heatmap_data.reindex(jours_attendus)  # Assurez-vous que les jours sont dans l'ordre attendu

        # Ajout d'un selectbox pour choisir la palette de couleurs
        palette_couleurs = st.selectbox(
            "Choisissez une palette de couleurs pour la heatmap :",
            options=["Viridis", "Cividis", "Blues", "Hot", "Plasma", "Turbo", "YlGnBu"],
            index=0  # Par défaut, "Viridis"
        )

        # Création de la heatmap interactive avec Plotly
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


    # ---- Graphique 3 : Évolution mensuelle des connexions ---- #
    with tab3:
        st.subheader("Temps de connexion cumulé selon le mois et l'année")

        # Extraction et regroupement des données
        wifi_usage_data["Année"] = wifi_usage_data["Date_début"].dt.year
        wifi_usage_data["Mois"] = wifi_usage_data["Date_début"].dt.month
        wifi_usage_data["Temps de sessions en minutes"] = pd.to_numeric(wifi_usage_data["Temps de sessions en minutes"], errors="coerce")
        temp = wifi_usage_data.groupby(['Année', 'Mois'], as_index=False)["Temps de sessions en minutes"].sum()

        # Filtrage interactif
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
            default=list(range(1, 13))  # Par défaut, tous les mois
        )
        temp_filtre = temp[
            (temp['Année'] >= plage_annees[0]) & 
            (temp['Année'] <= plage_annees[1]) & 
            (temp['Mois'].isin(mois_selectionnes))
        ]

        # Création du graphique
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




# ------------------- "Les utilisateurs" ------------------------------------------- #

# ---- Section "Les utilisateurs" ---- #
# ---- Section "Les utilisateurs" ---- #
elif menu == "Les utilisateurs 👩‍💻":
    st.title("Analyse des utilisateurs 👥")
    st.markdown("""
    Ce tableau fournit une analyse des utilisateurs des hotspots Wi-Fi par langue et leur évolution au fil des années. Il permet de visualiser les langues les plus utilisées ainsi que les tendances linguistiques en fonction des années d'utilisation, offrant un aperçu des comportements des utilisateurs.
    """)

    # Création des tabs pour les graphiques
    tab1, tab2 = st.tabs(["Connexions par langue", "Évolution des langues par année"])

    # ---- Graphique 1 : Nombre de connexions par langue d'utilisateur ---- #
    with tab1:
        st.subheader("Nombre de connexions par langue d'utilisateur")

        # ---- Corrections des langues ---- #
        corrections = {
            'Fran\x8dais': 'Français',
            'Fran‡ais': 'Français',
            'Chinois simplifi‚': 'Chinois simplifié',
            'Chinois simplifiŽ': 'Chinois simplifié',
            'Chinois traditionnel': 'Chinois traditionnel',
            'CorŽen': 'Coréen',
            'Cor‚en': 'Coréen',
            'NŽerlandais': 'Néerlandais',
            'N‚erlandais': 'Néerlandais',
            'Indon‚sien': 'Indonésien'
        }
        wifi_usage_data['Langue utilisateur'] = wifi_usage_data['Langue utilisateur'].replace(corrections)

        # ---- Ajout des images de drapeau ---- #
        langue_to_flag = {
            "Français": "https://upload.wikimedia.org/wikipedia/commons/c/c3/Flag_of_France.svg",
            "Anglais": "https://flagcdn.com/w40/gb.png",
            "Espagnol": "https://flagcdn.com/w40/es.png",
            "Chinois simplifié": "https://flagcdn.com/w40/cn.png",
            "Chinois traditionnel": "https://flagcdn.com/w40/tw.png",
            "Coréen": "https://flagcdn.com/w40/kr.png",
            "Néerlandais": "https://flagcdn.com/w40/nl.png",
            "Indonésien": "https://flagcdn.com/w40/id.png",
            "Allemand": "https://flagcdn.com/w40/de.png",
            "Italien": "https://flagcdn.com/w40/it.png",
            "Russe": "https://flagcdn.com/w40/ru.png",
            "Portugais": "https://flagcdn.com/w40/pt.png",
            "Arabe": "https://flagcdn.com/w40/sa.png",
            "Japonais": "https://flagcdn.com/w40/jp.png",
            "Polonais": "https://flagcdn.com/w40/pl.png",
            "Thaïlandais": "https://flagcdn.com/w40/th.png"
        }

        # Ajout d'une colonne "Drapeau"
        wifi_usage_data['Drapeau'] = wifi_usage_data['Langue utilisateur'].map(langue_to_flag)

        # Comptage des connexions par langue
        langue_data = wifi_usage_data['Langue utilisateur'].value_counts().reset_index()
        langue_data.columns = ['Langue', 'Nombre de connexions']
        langue_data['Drapeau'] = langue_data['Langue'].map(langue_to_flag)

        # ---- Filtrage interactif avec Streamlit ---- #
        langues_disponibles = langue_data['Langue'].tolist()
        langues_filtrees = st.multiselect(
            "Sélectionnez les langues à afficher :",
            options=langues_disponibles,
            default=langues_disponibles  # Par défaut, toutes les langues sont sélectionnées
        )

        # Filtrer les données en fonction des langues sélectionnées
        langue_data_filtre = langue_data[langue_data['Langue'].isin(langues_filtrees)]

        # ---- Graphique en barres avec drapeaux ---- #
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=langue_data_filtre['Langue'],
                y=langue_data_filtre['Nombre de connexions'],
                text=langue_data_filtre['Nombre de connexions'],
                textposition='outside',
                marker=dict(color='rgba(102, 197, 204, 0.7)', line=dict(color='rgba(102, 197, 204, 1.0)', width=1)),
            )
        )

        # Positionner les drapeaux uniquement pour les langues sélectionnées
        for i, row in langue_data_filtre.iterrows():
            fig.add_layout_image(
                dict(
                    source=row['Drapeau'],
                    x=i,
                    y=row['Nombre de connexions'] + max(langue_data_filtre['Nombre de connexions']) * 0.05,
                    xref="x",
                    yref="y",
                    sizex=0.6,
                    sizey=max(langue_data_filtre['Nombre de connexions']) * 0.07,
                    xanchor="center",
                    yanchor="bottom"
                )
            )

        fig.update_layout(
            title="Nombre de connexions par langue d'utilisateur",
            xaxis_title="Langues des utilisateurs",
            yaxis_title="Nombre de connexions",
            template="plotly_white",
            height=700,
        )

        st.plotly_chart(fig, use_container_width=True)

    # ---- Graphique 2 : Évolution des langues par année ---- #
    with tab2:
        st.subheader("Évolution des langues des utilisateurs par année")

        # ---- Extraction et création de la colonne Année ---- #
        wifi_usage_data["Date_début"] = pd.to_datetime(wifi_usage_data["Date_début"], errors="coerce")
        wifi_usage_data["Année"] = wifi_usage_data["Date_début"].dt.year

        # Filtrage des données
        min_annee, max_annee = int(wifi_usage_data['Année'].min()), int(wifi_usage_data['Année'].max())
        plage_annees = st.slider("Sélectionnez une plage d'années :", min_annee, max_annee, (min_annee, max_annee))

        df_filtre = wifi_usage_data[(wifi_usage_data['Année'] >= plage_annees[0]) & (wifi_usage_data['Année'] <= plage_annees[1])]

        if not df_filtre.empty:
            langue_par_annee = df_filtre.groupby(['Langue utilisateur', 'Année']).size().unstack(fill_value=0)
            total_frequence = langue_par_annee.sum(axis=1).sort_values(ascending=False)
            langue_par_annee = langue_par_annee.loc[total_frequence.index]
            langue_par_annee_normalisee = langue_par_annee.div(langue_par_annee.sum(axis=0), axis=1) * 100

            # Histogramme interactif avec Plotly
            fig = go.Figure()
            langues = langue_par_annee_normalisee.index
            annees = langue_par_annee_normalisee.columns

            for annee in annees:
                fig.add_trace(
                    go.Bar(
                        x=langues,
                        y=langue_par_annee_normalisee[annee],
                        name=f"{annee}"
                    )
                )

            fig.update_layout(
                barmode='group',
                title="Évolution des langues des utilisateurs",
                xaxis_title="Langues des utilisateurs",
                yaxis_title="Fréquence (%)",
                legend_title="Années",
                template="plotly_white"
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Aucune donnée disponible pour la plage d'années sélectionnée.")


#---------------------------Section "Appareils et leur Usages"-------------#

elif menu == "Les appareils et leurs usages 🤳🏼":
    # Titre de la page
    st.title("Analyse des appareils et des usages")
    st.markdown("""
    Cette section explore les appareils utilisés pour se connecter aux hotspots Wi-Fi et les types de données échangées. 
    Vous pourrez visualiser les volumes moyens échangés par appareil, la répartition des connexions par type de lieu et appareil, ainsi que les usages principaux des connexions Wi-Fi.
    """)

    # Création des onglets pour les graphiques
    tab1, tab2, tab3 = st.tabs(["Volumes moyens par appareil", "Connexions par lieu et appareil", "Connexions par lieu et usage"])

    # ---- Graphique 1 : Volumes moyens par appareil ---- #
    with tab1:
        st.subheader("Volumes moyens de données échangées par appareil")
        # Calcul des volumes moyens
        data_volume = wifi_usage_data.groupby("Type d'appareil")[["Donnée entrante (MégaOctet)", "Donnée sortante (MégaOctet)"]].mean()

        # Création du graphique
        ax = data_volume.plot(
            kind="bar",
            figsize=(24, 12),
            stacked=True,
            color=["steelblue", "orange"]
        )

        # Titres et légendes
        plt.title("Volume moyen de données échangées par type d'appareil", fontsize=20, weight="bold")
        plt.xlabel("Type d'appareil", fontsize=16, weight="bold")
        plt.ylabel("Volume moyen (MégaOctet)", fontsize=16, weight="bold")
        plt.xticks(rotation=45, ha="right", fontsize=14)
        plt.yticks(fontsize=14)
        plt.legend(
            ["Données entrantes (Téléchargées)", "Données sortantes (Envoyées)"], 
            title="Type de données", 
            fontsize=14, 
            title_fontsize=16
        )

        # Ajout des valeurs pour chaque barre
        for i, bars in enumerate(ax.containers):
            for bar in bars:
                x = bar.get_x() + bar.get_width() / 2  # Position horizontale
                y = bar.get_height()  # Hauteur de la barre
                if y > 0:  # Si la hauteur est positive
                    if i == 0:  # Barres bleues (données entrantes)
                        ax.text(
                            x, 
                            bar.get_y() + y / 2,  # Garder la position initiale
                            f"{y:.1f}", 
                            ha="center", 
                            va="center", 
                            fontsize=12, 
                            weight="bold", 
                            color="white"
                        )
                    elif i == 1:  # Barres orange (données sortantes)
                        ax.text(
                            x, 
                            bar.get_y() + bar.get_height(),  # Position au-dessus de la barre
                            f"{y:.1f}", 
                            ha="center", 
                            va="bottom", 
                            fontsize=12, 
                            weight="bold", 
                            color="black"
                        )

        plt.tight_layout()
        st.pyplot(plt)  # Afficher le graphique dans Streamlit

    # ---- Graphique 2 : Répartition des connexions par type de lieu et appareil ---- #

    with tab2:
        st.subheader("Répartition des connexions par type de lieu et appareil")
        
        # Conversion des noms de sites en majuscules
        wifi_usage_data["Nom du Site"] = wifi_usage_data["Nom du Site"].str.upper()

        # Fonction pour catégoriser les lieux
        def categories_lieu(lieu):
            if any(substring in lieu for substring in ["BIBLIOTHEQUE", "MEDIATHEQUE"]):
                return "Bibliothèques"
            elif any(substring in lieu for substring in ["MAIRIE", "HOTEL", "BOURSE", "SYSTEME", "EMPLOI"]):
                return "Lieux administratifs"
            elif any(substring in lieu for substring in [
                "KIOSQUE", "JEUNES", "ARTISANALES", "INSERTION", "MAISON",
                "ESPACE", "CAPLA", "EPI", "INITIATIVES", "CLIMAT", "ASSOCIA"
            ]):
                return "Equipements culturels"
            elif "FOURRIERE" in lieu:
                return "Fourrières"
            elif any(substring in lieu for substring in ["PARC", "SQUARE", "JARDIN", "VERTE", "BERGE", "PROMENADE"]):
                return "Espaces verts"
            elif any(substring in lieu for substring in ["SPORTIF", "GYMNASE", "PISCINE", "STADE", "NAUTIQUE", "GLISSE", "CS"]):
                return "Equipements sportifs"
            elif any(substring in lieu for substring in ["CATACOMBES", "INVALIDES", "CRYPTE", "MUSEE", "ARCHIVE"]):
                return "Monuments"
            else:
                return "Autres"

        # Appliquer la fonction
        wifi_usage_data["lieu_types"] = wifi_usage_data["Nom du Site"].fillna("").apply(categories_lieu)

        # Créer l'histogramme
        custom_colors = {
            "Mobile": "#636EFA",
            "Ordinateur": "#EF553B",
            "Tablette": "#00CC96"
        }

        fig = px.histogram(
            wifi_usage_data,
            x="lieu_types",
            color="Type d'appareil",
            title="<b>Répartition des connexions par type de lieu et appareil</b>",
            labels={"lieu_types": "Type de lieux", "Type d'appareil": "Type d'appareil"},
            barmode="stack",
            color_discrete_map=custom_colors
        )

        # Personnalisation
        fig.update_layout(
            width=1000,
            height=700,
            xaxis_title="<b>Type de lieux</b>",
            yaxis_title="<b>Nombre de connexions</b>",
            legend_title="<b>Type d'appareil</b>",
            template="plotly_white",
            yaxis=dict(tickmode="linear", tick0=0, dtick=20000, range=[0, 140000])
        )
        st.plotly_chart(fig)

    # ---- Graphique 3 : Répartition des connexions par type de lieu et usage ---- #
    with tab3:
        st.subheader("Répartition des connexions par type de lieu et usage")

        fig = px.histogram(
            wifi_usage_data,
            x="lieu_types",
            color="Type d'usage",
            title="<b>Répartition des connexions par type de lieu et type d'usage</b>",
            labels={"lieu_types": "Type de lieux", "Type d'usage": "Type d'usage", "y": "Nombre de connexions"},
            color_discrete_map={
                "consultation": "#003f5c",
                "upload": "#ffa600"
            }
        )

        # Ajouter les valeurs au-dessus des barres
        fig.update_traces(
            texttemplate='%{y:,}',  
            textposition='outside'  
        )

        fig.update_layout(
            barmode="stack",
            xaxis_title="<b>Type de lieux</b>",
            yaxis_title="<b>Nombre de connexions</b>",
            legend_title="<b>Type d'usage</b>",
            width=1000,
            height=700,
            template="plotly_white",
            yaxis=dict(tickmode="linear", tick0=0, dtick=20000, range=[0, wifi_usage_data.groupby("lieu_types").size().max() + 20000])
        )
        st.plotly_chart(fig)


