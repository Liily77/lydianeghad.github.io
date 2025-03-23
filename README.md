### **🔹 Projet : Power BI & Azure – Analyse de l’entreprise Meublatex 🛋️📊**

👉 [Voir le projet ici](https://github.com/Liily77/lydianeghad.github.io/tree/Projet_PowerBI_Azure)

**Description :**  
Dans ce projet, nous avons mis en place un système décisionnel pour une entreprise fictive de vente de meubles (**Meublatex**), combinant des compétences de **Data Engineering** et **Data Analytics**. 

Le projet se déroule en deux phases : ingestion et transformation des données via **Azure Data Factory**, puis visualisation et analyse avec **Power BI**.

**Phase 1 – Data Engineering :**  

◾ Stockage des fichiers sources (ventes, clients, magasins, produits, dépenses) dans un **Data Lake Azure**.  
◾ Création d’un **ODS** pour les données brutes.  
◾ Alimentation d’un **Data Warehouse** nettoyé via **Azure Data Factory**.  
◾ Construction de **Master Pipelines** :  

&nbsp;&nbsp;&nbsp;&nbsp;• `Master_Pipeline_ODS`  
&nbsp;&nbsp;&nbsp;&nbsp;• `Master_Pipeline_DWH`  
&nbsp;&nbsp;&nbsp;&nbsp;• `Master_Pipeline` (global)  

**Phase 2 – Data Analytics :** 

◾ Création d’un **rapport Power BI interactif** avec plusieurs pages :  

- **Accueil** : carte des magasins, CA global, analyse temporelle  
- **Analyse produits** : top produits vendus, marge  
- **Analyse clients** : clients les plus rentables  
- **Analyse dépenses** : ventilation par catégorie  
- **Analyse bénéfices** : revenus vs charges
  
◾ Utilisation de **DAX** pour construire des **KPI dynamiques**.  
◾ Filtres interactifs, slicers et segmentations avancées pour une exploration par période, magasin, produit, etc.

**🛠️ Technologies :**  
Azure Data Factory, Azure Data Lake, Power BI, SQL, DAX, Git
