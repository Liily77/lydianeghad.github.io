# 🧠 Projet Neo4j : Procédures stockées pour réseau de neurones graphé 🚀

## 🔄 Contexte

Ce projet est basé sur le dépôt du professeur :  
👉 [https://github.com/miyasiffaye/neo4j-cours](https://github.com/miyasiffaye/neo4j-cours)

Nous avons cloné ce dépôt pour y **ajouter des fichiers `.java` compilés en `.class`**, correspondant à des **procédures stockées Cypher** destinées à être utilisées dans Neo4j pour construire et entraîner un réseau de neurones.

## 🎯 Objectifs

- Transformer les requêtes Cypher du script Python initial en **procédures stockées Java**.
- Améliorer la modularité, les performances et la réutilisabilité des étapes du modèle de réseau de neurones.
- Intégrer ces procédures dans Neo4j pour une exécution directe via l’interface ou les scripts Python.

## 📁 Structure du projet

Les fichiers `.class` ajoutés dans le projet représentent les principales étapes de l’entraînement d’un réseau de neurones :

- `CreateNetwork.class`, `CreateNeuron.class`, `CreateInputsRowNode.class`, etc.  
  → Création de la structure du réseau (couches, neurones, entrées, sorties)

- `SetInputs.class`, `SetExpectedOutputs.class`  
  → Chargement des données dans Neo4j

- `ForwardPass.class`, `BackwardPassAdam.class`, `ComputeLoss.class`, etc.  
  → Exécution du passage avant, calcul de la perte et rétropropagation avec l’optimiseur Adam

- `ConstrainWeights.class`  
  → Application de contraintes sur les poids

Chaque classe dispose également d’une version `*Result.class` pour la gestion des retours d’exécution.


## 🔧 Technologies utilisées

- **Neo4j** : Base de données orientée graphe
- **Java** : Implémentation des procédures stockées personnalisées
- **Cypher** : Langage de requêtes Neo4j
- **Python** : Pour le script principal (fourni par le professeur)
- **Git** : Gestion de versions et collaboration
- **Maven / Gradle** (optionnel) : Compilation des fichiers Java

---

## ✅ Étapes réalisées

- ✅ Clonage du dépôt de base
- ✅ Implémentation des procédures Java
- ✅ Compilation des classes
- ✅ Ajout des fichiers `.class` au projet
- ✅ Test via les appels depuis Neo4j Desktop ou les scripts Python


## 📌 Pour lancer le projet

1. Cloner ce dépôt  
2. Lancer Neo4j Desktop avec le plugin APOC activé  
3. Importer les procédures compilées dans le dossier `plugins/` de Neo4j  
4. Redémarrer la base  
5. Utiliser les procédures via Cypher ou les scripts Python fournis



