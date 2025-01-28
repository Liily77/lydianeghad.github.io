# 🚀 **Projet Spark Scala : Pipeline de Traitement et Analyse de Données**

## 🖋️ **Description**
Ce projet utilise **Scala** et **Apache Spark** pour automatiser un **pipeline de traitement de données**. L'objectif est de manipuler, transformer et analyser des ensembles de données complexes tout en respectant une structure modulaire et des bonnes pratiques d'ingénierie des données.

---

## ✔️ **Objectifs principaux**
- **Extraction** : Lecture de fichiers **CSV**, **JSON**, **XML**.
- **Nettoyage** : Harmonisation des formats et gestion des valeurs manquantes.
- **Transformation** : Création de nouvelles colonnes (**TTC**, **Statut Contrat**).
- **Analyse** : Agrégation et génération d'insights.
- **Validation** : Tests unitaires avec **ScalaTest**.

---

## 💻 **Technologies utilisées**
- **Scala** : Langage principal.
- **Apache Spark** : Framework pour le traitement distribué.
- **SBT** : Outil de build et gestion des dépendances.
- **ScalaTest** : Framework de tests unitaires.
- **Log4j2** : Gestion des logs.

---

## 📂 **Structure du projet**
- **main/MainBatch** : Point d'entrée du pipeline.
- **args/Args** : Paramètres et arguments du programme.
- **parser/** : Analyse des fichiers **JSON**, **CSV**, **XML**.
- **reader/** : Classes de lecture des données.
- **traitement/ServiceVente** : Transformation des données.
- **test/** : Tests unitaires avec **ScalaTest**.
- **build.sbt** : Configuration des dépendances.

---

## 📊 **Aperçu des analyses réalisées**
- Calcul et structuration des données par **Statut de Contrat**.
- Agrégation des métriques clés (**Moyenne TTC**, **Nombre de contrats**).
- Validation des transformations avec des jeux de données tests.

---

## 💪 **Ce que j'ai appris**
- Automatisation d'un **pipeline de données Spark**.
- Manipulation avancée de **DataFrames**.
- Gestion des fichiers multi-formats (**CSV**, **JSON**, **XML**).
- Développement modulaire et optimisé avec **Scala** et **SBT**.

---

## 🎯 **Difficultés rencontrées et solutions**
- **Formatage des fichiers :** Gestion des types hétérogènes → Nettoyage avec **Spark SQL**.
- **Agrégation des données :** Structure complexe des données → Aplatissement des colonnes JSON/XML.
- **Validation des résultats :** Tests robustes avec **ScalaTest**.

