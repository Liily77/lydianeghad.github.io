# 📘 Mémoire Data Engineering – Détection de clients influents dans l’hôtellerie

## 🏨 Contexte
Ce mémoire s’inscrit dans une logique exploratoire de data engineering appliquée au secteur de l’hôtellerie. La chaîne **Best Western** est choisie comme cadre d’étude.  
Face à l’impact croissant des avis clients en ligne (TripAdvisor, Google Reviews...), il devient stratégique pour les établissements hôteliers d’identifier les **clients dits “centraux”**, c’est-à-dire ceux qui publient fréquemment des avis ou possèdent une certaine influence numérique.  
**Par souci de faisabilité et de qualité des données disponibles, nous nous concentrons sur TripAdvisor, une des principales plateformes d’avis en hôtellerie, conforme aux attentes du sujet.**

## 🎯 Objectifs
- Collecter automatiquement des avis clients depuis des plateformes publiques
- Construire un pipeline de données (scraping → stockage → transformation → visualisation)
- Détecter les clients influents à l’aide d’indicateurs de centralité
- Mettre en place une architecture évolutive et automatisée de suivi
- Fournir un dashboard interactif de supervision des avis

## ❓ Problématique
Comment construire un pipeline de traitement de données à partir d’avis clients en ligne, dans le but d’identifier automatiquement les clients les plus influents d’une chaîne hôtelière ?

## ✅ Livrables attendus
- Scripts Python pour scraping, traitement et chargement
- Jeu de données brut et nettoyé (CSV ou Parquet)
- Architecture Data Lake simulée (Delta Lake local)
- Pipeline automatisé (GitHub Actions ou script planifié)
- Dashboard (Streamlit ou Power BI)
- Mémoire rédigé avec explications techniques et analyse des résultats

## 🔧 Technologies prévues
- Python (scraping, traitement)
- BeautifulSoup, Requests (ingestion)
- PySpark / dbt (transformation)
- Delta Lake / Parquet (stockage)
- Streamlit / Power BI (visualisation)
- Git & GitHub Actions (automatisation)
