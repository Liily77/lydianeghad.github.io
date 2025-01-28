# Projet Databricks : Analyse Scala et PySpark 🚀

👉 [Voir le projet ici](https://lydianeghad.alwaysdata.net/databricks/index.html)

## Description 🖋️

Ce projet a été réalisé sur **Databricks** en utilisant Scala et PySpark pour analyser des données complexes et effectuer des calculs avancés. L'objectif était de manipuler, transformer et visualiser les données en respectant les consignes du sujet fourni.

## Objectifs principaux ✔️

1. Chargement et traitement des données JSON.
2. Création de cubes de données pour analyse multi-dimensionnelle.
3. Réalisation d'analyses croisées entre étudiants et professeurs.
4. Mise en place d'un système de priorisation et d'organisation des résultats.
5. Génération de visualisations et tri logique des résultats.

## Technologies utilisées 💻

- **Databricks** : Plateforme collaborative pour l'analyse de données à grande échelle.
- **Scala** et **PySpark** : Langages utilisés pour manipuler et analyser les données.
- **SQL** : Pour les requêtes et analyses croisées.
- **JSON** : Format des données sources.

## Contenu du projet 📂

- **[HTML interactif](https://github.com/Liily77/lydianeghad.github.io/blob/Databricks_Scala_Project/Projet%20Databricks%20Lydia.html)** : Code complet et analyses exportées depuis Databricks.
- **Sujet PDF** : Les consignes et objectifs du projet (disponible dans le dépôt).
- **Données JSON** : Données sources utilisées pour l'analyse.

## Aperçu des analyses réalisées 📊

1. **Calcul des cubes multidimensionnels** :
   
   - Analyse des données étudiantes et des bourses.
   - Organisation des résultats par universités et années avec priorisation (`All_Years`, `All_Univ`).
     
2. **Analyse croisée des étudiants et professeurs** :
   
   - Association des professeurs selon leurs cours.
   - Gestion des cas où aucun professeur n'est associé (`Profs_No_Recompensés`).
     
3. **Tri logique des résultats** :
   
   - Ordre personnalisé pour une meilleure lisibilité.
   - Visualisation des données dans un format clair et structuré.

## Ce que j'ai appris 💪
- **Manipulation des données** avec PySpark et Scala.
- **Analyse des relations** entre entités (étudiants et professeurs).
- **Structuration des résultats** avec SQL et transformations Spark.
- **Développement collaboratif** sur une plateforme comme Databricks.

## Difficultés rencontrées et solutions 🎯

1. **Données ambiguës** :
   
   - Problème : Colonnes avec des noms identiques (`Annee`).
   - Solution : Renommer les colonnes pour éviter les conflits.
     
2. **Organisation des résultats** :
   
   - Problème : Tri logique des données.
   - Solution : Création de colonnes spécifiques comme `orderIndex` pour gérer l'ordre.
     
3. **Validation des cas limites** :
   
   - Problème : Association des professeurs pour des cas particuliers.
   - Solution : Utilisation de jointures spécifiques et gestion des valeurs nulles.


