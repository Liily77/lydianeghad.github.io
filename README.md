# Projet : Analyse de données avec Databricks 🚀

## Description du projet 🖋️

Ce projet a été réalisé dans le cadre de l'analyse des données grâce à Databricks et PySpark. Il vise à manipuler et visualiser des données afin de répondre à diverses questions analytiques, comme l'extraction d'informations spécifiques, la mise en relation des données, ou encore la création de visualisations claires. 

Les étapes du projet incluent :
- Chargement et traitement des données JSON fournies.
- Application des transformations et calculs pour répondre aux besoins analytiques.
- Création de visualisations pour explorer les données et en tirer des insights.

## Contenu des fichiers 📂

 1. **`Data_TP2_MSD`**  
Fichier JSON contenant les données sources. Il inclut deux ensembles de données principaux :
- **Etudiants** : Données relatives aux étudiants, telles que leurs bourses, universités, et formations.
- **Profs** : Données sur les professeurs, leurs formations associées et les années correspondantes.

 2. **`Projet Databricks Lydia`**  
Lien HTML pour visualiser le code exécuté et les résultats obtenus directement depuis Databricks.

 3. **`Sujet projet Databricks`**  
Document PDF décrivant les consignes du projet et les objectifs à atteindre, avec les questions détaillées.

## Objectifs atteints ✔️

- **Chargement et exploration des données JSON** :
  - Exploitation des fichiers avec PySpark pour effectuer des calculs et transformations.
- **Jointures et agrégations** :
  - Association entre étudiants et professeurs pour déterminer les correspondances et les absences de correspondances.
- **Création de cubes de données** :
  - Mise en place d'agrégations avec des cubes multidimensionnels pour analyser les données en fonction des universités et des années.
- **Calculs avancés** :
  - Mise en ordre des données grâce à des index personnalisés et résolution des valeurs manquantes avec des catégories par défaut.
- **Visualisations** :
  - Production de graphiques à partir des données agrégées et classées.

## Technologies utilisées 💻

- **Databricks** : Plateforme principale pour l'exécution et l'analyse.
- **PySpark** : Manipulation des données massives.
- **SQL** : Extractions et transformations analytiques.
- **JSON** : Format des données sources.

## Compétences acquises 🎯

- Traitement des données structurées et semi-structurées.
- Jointures avancées entre différents ensembles de données.
- Utilisation des cubes OLAP pour l'agrégation multidimensionnelle.
- Création de pipelines de données pour répondre à des besoins spécifiques.
- Visualisation des données et storytelling.

## Difficultés rencontrées et solutions apportées 🌟

### Problème : Gestion des doublons et des colonnes ambiguës  
Certaines jointures ont généré des erreurs dues à des noms de colonnes similaires ou à des doublons.  
**Solution :**  
- Renommage des colonnes pour éviter les ambiguïtés.  
- Suppression des doublons avec `.dropDuplicates()`.

### Problème : Absence de données dans certaines colonnes  
Certaines valeurs étaient nulles dans les résultats des jointures.  
**Solution :**  
- Remplacement des valeurs nulles par des catégories par défaut, comme `"Profs_No_Recompensés"`.

### Problème : Classement des données selon un ordre personnalisé  
L'ordre attendu par le projet ne correspondait pas à l'ordre naturel des données.  
**Solution :**  
- Ajout d'une colonne `orderIndex` pour contrôler l'ordre et tri final avec `.orderBy()`.



Merci de votre lecture ! 🌟

