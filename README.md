# 🎬 Projet Machine Learning : Analyse de Sentiments des Films Oscar (2020-2024) 🚀

## Description 🖋️

Ce projet applique le **Machine Learning** pour analyser les **avis** sur les films nommés ou récompensés aux **Oscars** entre **2020 et 2024**.  
L'objectif est de classifier les critiques en **positives, négatives ou neutres**, tout en explorant les tendances et en fournissant des insights exploitables.

## Objectifs principaux ✔️

1. **Extraction** : Collecte de critiques issues de **Allociné, IMDb, Rotten Tomatoes**.  
2. **Nettoyage** : Suppression du bruit, gestion des emojis, tokenization et normalisation.  
3. **Feature Engineering** : Vectorisation des critiques avec **TF-IDF, Word2Vec et embeddings pré-entraînés**.  
4. **Modélisation** : Entraînement de modèles de classification (**Logistic Regression, Random Forest, LSTM**).  
5. **Évaluation** : Validation des performances avec des métriques adaptées (**Accuracy, F1-score**).  
6. **Visualisation** : Analyse des **tendances de notation et d'opinion** par année et catégorie de film.  

## Technologies utilisées 💻

- **Python** : Langage principal.  
- **Scikit-learn** : Implémentation des modèles de Machine Learning.  
- **NLTK / SpaCy** : Prétraitement du texte.  
- **TensorFlow / PyTorch** : Entraînement de modèles avancés.  
- **Matplotlib / Seaborn** : Visualisation des résultats.  
- **Flask / FastAPI** : API pour exposer le modèle en production.  


## Aperçu des analyses réalisées 📊

- **Distribution des sentiments** des critiques par film et par année.  
- **Analyse des tendances** : Évolution des opinions sur les films oscarisés.  
- **Comparaison des performances** des modèles de classification.  
- **Impact des récompenses** sur la perception du public (avant/après les Oscars).  

## Ce que j'ai appris 💪

- **Prétraitement avancé de texte** pour l'analyse de sentiments.  
- **Optimisation des hyperparamètres** des modèles de classification.  
- **Manipulation d'outils de visualisation** pour l'analyse des critiques.  
- **Mise en production** d’un modèle de Machine Learning avec une API.  

## Difficultés rencontrées et solutions 🎯

1. **Données non structurées** :
   - **Problème** : Variabilité dans la structure des critiques selon les sources.  
   - **Solution** : Normalisation des textes avec **Regex, NLP et lemmatisation**.  

2. **Déséquilibre des avis** :
   - **Problème** : Certains films ont **beaucoup plus de critiques positives que négatives**.  
   - ✅ **Solution** : Utilisation de techniques de **sur-échantillonnage (SMOTE)** et **sous-échantillonnage**.  

3. **Compréhension des modèles** :
   - **Problème** : Interprétation des décisions des modèles complexes.  
   - **Solution** : Utilisation de **SHAP** et **LIME** pour expliquer les prédictions.  
