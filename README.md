# Projet : Analyse des Hotspots Wi-Fi à Paris 🌐

👉 [Voir l'application Streamlit ici](https://hotpost-wifi-paris-project.streamlit.app/)

![Capture d'écran de l'application](capture_ecran.png)

## Exemples de visualisations :
- Répartition des connexions par arrondissement.
- Cartographie des hotspots avec volume de connexions.
- Heatmap temporelle des connexions Wi-Fi.
- Répartition des connexions par appareil et usage.
- Visualisation WordCloud des concepts principaux.

## Description 🖋️

Ce projet Python vise à explorer et analyser les données d'utilisation des hotspots Wi-Fi à Paris. L'application Streamlit offre des visualisations interactives pour examiner les tendances géographiques, temporelles, et comportementales, ainsi que des analyses plus spécifiques comme les usages par appareil ou par type d'usage.

## Structure du projet 💡
Le projet est structuré en plusieurs sections :
- **Origine des données** : Présentation des données et aperçu des variables.
- **Analyse géographique** : Répartition par arrondissement et visualisation sur une carte interactive.
- **Analyse temporelle** : Variations annuelles, heatmap par jour/heure et évolution mensuelle des connexions.
- **Analyse des utilisateurs** : Langues utilisées et tendances par année.
- **WordCloud** : Représentation visuelle des mots-clés dans les données textuelles.

## Technologies utilisées 💻
- **Python** : Langage principal utilisé pour l'analyse et la création de l'application.
- **Pandas** : Pour la manipulation et l'analyse des données tabulaires.
- **Plotly** : Pour des visualisations interactives comme les cartes et les graphiques.
- **Seaborn** et **Matplotlib** : Pour des visualisations analytiques et statistiques.
- **Streamlit** : Framework pour créer une interface utilisateur interactive et déployer l'application.

## Compétences acquises ✔️
- **Exploration de données** : Analyse, transformation et visualisation des données avec Pandas.
- **Visualisations interactives** : Création de graphiques dynamiques et intuitifs avec Plotly.
- **Développement d'application** : Création d'une interface utilisateur avec Streamlit.
- **Storytelling avec les données** : Présentation claire et visuelle des insights pour un public non technique.

## Ce que j'ai appris 💪
- **Nettoyage et transformation des données** : Préparer les données brutes pour les rendre exploitables.
- **Visualisation avancée** : Maîtrise des outils comme Plotly et Seaborn.
- **Développement full-stack léger** : Conception d'une application complète avec Streamlit.
- **Analyse des tendances** : Identifier des patterns dans les données pour mieux comprendre l'utilisation des hotspots Wi-Fi.

## Difficultés rencontrées et solutions 🎯
- **Données complexes à manipuler :** Certaines colonnes contenaient des formats inattendus ou des valeurs manquantes.
  - **Solution :** Utilisation des fonctions de nettoyage de Pandas, comme `pd.to_datetime` pour les dates ou `fillna()` pour les valeurs manquantes.
- **Création des visualisations interactives :** Rendre les graphiques intuitifs tout en manipulant des datasets volumineux.
  - **Solution :** Optimisation avec Plotly et ajustement des paramètres pour des performances optimales.
- **Personnalisation des sections WordCloud et géographiques :** Ajouter un masque pour le WordCloud et intégrer une carte interactive.
  - **Solution :** Expérimentation avec les bibliothèques WordCloud et Mapbox pour répondre aux besoins du projet.
- **Déploiement sur Streamlit Cloud :** Problèmes avec les dépendances non installées.
  - **Solution :** Mise à jour du fichier `requirements.txt` avec toutes les bibliothèques nécessaires.

## Organisation des fichiers 📂
- **app.py** : Code principal de l'application Streamlit.
- **requirements.txt** : Dépendances Python à installer.
- **README.md** : Documentation du projet.
- **Projet Data Viz.ipynb** : Analyses préliminaires sous Jupyter Notebook.
- **assets/** : Images et fichiers supplémentaires.
- **.streamlit/** : Paramètres de configuration Streamlit.

