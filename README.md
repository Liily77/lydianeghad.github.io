<h1 align="center">Portfolio</h1>

<p>Bienvenue sur mon portfolio ! Ici, vous trouverez une sélection de mes projets réalisés dans le cadre de mes études, ainsi que de mes expérimentations personnelles en développement web et en data analytics. 
Chaque projet met en avant mes compétences dans ces deux domaines, illustrant ma polyvalence et ma passion pour le code et l'analyse des données.</p>


<h2 align="center">📈 Mes projets en Data</h2>
<br>

### **🔹 Projet : 🧠 Neo4j - Procédures stockées pour réseau de neurones graphé 🚀**

👉 [Voir le projet ici](https://github.com/Liily77/lydianeghad.github.io/tree/Projet_Neo4J)

**Description :**  
Ce projet s'appuie sur un dépôt académique que nous avons enrichi par l'ajout de **procédures stockées en Java** pour **Neo4j**, dans le but de modéliser et entraîner un réseau de neurones directement dans une base orientée graphe. Les requêtes Cypher ont été encapsulées dans des classes Java compilées pour plus de modularité et de performance.

**Objectifs principaux :**

◾ Transformer des scripts Cypher en **procédures stockées Java**.  
◾ **Créer et configurer** un réseau de neurones (couches, neurones, entrées/sorties).  
◾ **Charger des données d'entrée** et **sortie attendue** dans Neo4j.  
◾ Implémenter le **passage avant**, la **rétropropagation avec Adam**, et le **calcul de la perte**.  
◾ Gérer les **résultats et contraintes sur les poids** via des classes spécialisées.  

**Structure des classes :**  
- `CreateNetwork.class`, `CreateNeuron.class`, `SetInputs.class`, etc.  
- `ForwardPass.class`, `BackwardPassAdam.class`, `ComputeLoss.class`, etc.  
- Chaque fichier `.class` a sa version `*Result.class` pour le retour d'exécution.

**🛠️ Technologies :** Neo4j, Java, Cypher, Python, Git, IntelliJ, Maven/Gradle

<p align="center">
  <img src="https://dist.neo4j.com/wp-content/uploads/20201006110518/neo4j-logo-1.svg" alt="Neo4j" width="100" height="60" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/java/java-original.svg" alt="Java" width="60" height="60" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/git/git-original.svg" alt="Git" width="60" height="60" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/intellij/intellij-original.svg" alt="IntelliJ" width="60" height="60" />
</p>

<br>

### **🔹 Projet : Pipeline de traitement et analyse de données avec Spark et Scala 🚀**

👉 [Voir le projet ici](https://github.com/Liily77/lydianeghad.github.io/tree/spark-data-pipeline)

**Description :**  
Ce projet utilise **Scala** et **Apache Spark** pour automatiser un pipeline de traitement de données. L'objectif était de manipuler, transformer et analyser des ensembles de données complexes tout en respectant une structure modulaire et des bonnes pratiques d'ingénierie des données.  
Les analyses incluent l'extraction, le nettoyage, la transformation et l'agrégation des données avec validation par tests unitaires.

**Objectifs principaux :**  

◾ **Extraction** : Lecture et ingestion de fichiers **CSV, JSON, XML**.  
◾ **Nettoyage** : Harmonisation des formats et gestion des **valeurs manquantes**.  
◾ **Transformation** : Création de nouvelles colonnes (**TTC, Statut Contrat**).  
◾ **Analyse** : Agrégation des données et génération d'**insights**.  
◾ **Validation** : Mise en place de **tests unitaires** avec **ScalaTest**.  

**🛠️ Technologies :** Scala, Apache Spark, Spark SQL, SBT, ScalaTest, Log4j2

<p align="center">
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/scala/scala-original.svg" alt="Scala" width="60" height="60" />
  <img src="https://upload.wikimedia.org/wikipedia/commons/f/f3/Apache_Spark_logo.svg" alt="Apache Spark" width="120" height="60" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/sqlite/sqlite-original.svg" alt="SQL" width="60" height="60" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/json/json-original.svg" alt="JSON" width="60" height="60" />
</p>

<hr>

### **🔹 Projet : Analyse scala et PySpark sur databricks 🚀**

👉 [Voir le projet ici](https://github.com/Liily77/lydianeghad.github.io/tree/Databricks_Scala_Project)

**Description :**  
Ce projet a été réalisé sur **Databricks** avec **Scala** et **PySpark** pour analyser des données complexes. L'objectif était de manipuler, transformer et visualiser les données efficacement, en créant des cubes de données et en réalisant des analyses croisées entre étudiants et professeurs.

**Objectifs principaux :** 

◾ **Chargement et traitement** des données **JSON**.  
◾ **Création de cubes de données** pour **analyse multi-dimensionnelle**.  
◾ **Réalisation d'analyses croisées** entre **étudiants et professeurs**.  
◾ **Mise en place d'un système de priorisation** et **organisation des résultats**.  
◾ **Génération de visualisations** et **tri logique des résultats**.  


**🛠️ Technologies :** Scala, PySpark, SQL, JSON, Databricks

<p align="center">
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/scala/scala-original.svg" alt="Scala" width="60" height="60" />
  <img src="https://upload.wikimedia.org/wikipedia/commons/f/f3/Apache_Spark_logo.svg" alt="PySpark" width="120" height="60" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/sqlite/sqlite-original.svg" alt="SQL" width="60" height="60" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/json/json-original.svg" alt="JSON" width="60" height="60" />
</p>


<hr>

### **🔹 Projet : Machine Learning - Analyse de sentiments des films oscars (2020-2024) 🎬**

👉 [Voir le projet ici](https://github.com/Liily77/lydianeghad.github.io/tree/projet_machine_learning)

**Description :**  
Ce projet applique le **Machine Learning** pour analyser les **avis** sur les films nommés ou récompensés aux **Oscars** entre **2020 et 2024**.  
L'objectif est de classifier les critiques en **positives, négatives ou neutres**, tout en explorant les tendances et en fournissant des insights exploitables.

**Objectifs :**  

◾ **Collecte et nettoyage** des critiques issues de **Allociné, IMDb, Rotten Tomatoes**  
◾ **Feature Engineering** avec **TF-IDF, Word2Vec et embeddings pré-entraînés**  
◾ **Entraînement de modèles** : **Logistic Regression, Random Forest, LSTM**  
◾ **Évaluation des performances** avec **Accuracy, F1-score**  
◾ **Analyse des tendances de notation et d'opinion**  

**🛠️ Technologies :**  

<p align="center">
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" alt="Python" width="60" height="60"/>
  <img src="https://upload.wikimedia.org/wikipedia/commons/0/05/Scikit_learn_logo_small.svg" alt="Scikit-learn" width="60" height="60"/>
  <img src="https://upload.wikimedia.org/wikipedia/commons/2/2d/Tensorflow_logo.svg" alt="TensorFlow" width="60" height="60"/>
  <img src="https://seaborn.pydata.org/_images/logo-tall-lightbg.svg" alt="Seaborn" width="60" height="60"/>
  <img src="https://upload.wikimedia.org/wikipedia/commons/3/3c/Flask_logo.svg" alt="Flask" width="80" height="60"/>
</p>
<hr>

### **🔹 Projet : Analyse des Hotspots Wi-Fi à Paris 🌐**

👉 [Voir l'application Streamlit ici](https://hotpost-wifi-paris-project.streamlit.app/)

**Description :**  
Ce projet Python vise à explorer et analyser les données d'utilisation des hotspots Wi-Fi à Paris, en mettant en avant des tendances géographiques, temporelles et comportementales. L'application Streamlit propose des visualisations interactives pour examiner les connexions, les appareils, les langues utilisées et les usages.

👉 [Accéder à la branche du projet](https://github.com/Liily77/lydianeghad.github.io/tree/Streamlit)

**Objectifs principaux :**  

◾ **Analyse géographique** : Répartition des connexions **par arrondissement** et **cartographie interactive**.  
◾ **Analyse temporelle** : Évolution des connexions par année, heatmap des connexions **par jour et par heure**.  
◾ **Analyse des utilisateurs** : Répartition des **langues utilisées** et **tendances d'usage**.  
◾ **WordCloud interactif** : Représentation visuelle des **concepts principaux** dans les données textuelles.  
◾ **Déploiement d’une application interactive** avec **Streamlit** pour la **data visualisation**. 

**🛠️ Technologies :** Python, Pandas, Plotly, Streamlit

<p align="center">
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" alt="Python" width="60" height="60" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/pandas/pandas-original-wordmark.svg" alt="Pandas" width="60" height="60" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/plotly/plotly-original.svg" alt="Plotly" width="60" height="60" />
  <img src="https://streamlit.io/images/brand/streamlit-mark-light.svg" alt="Streamlit" width="120" height="60" />
</p>

<hr>

<h3><strong>🔹 Projet : Analyse des performances des rameurs 🚣‍♂️📊</strong></h3>

👉 [Voir le notebook ici](https://github.com/Liily77/lydianeghad.github.io/blob/Analyse-Donn%C3%A9es-Sportives/analyse-rameurs.ipynb)

**Description :**  
Ce projet Python vise à analyser les performances des rameurs sur une distance de 2000m, segmentée par portions de 500m. À travers des visualisations interactives et des analyses avancées, nous avons exploré les facteurs influençant les performances et comparé les rameurs entre eux.

👉 [Accéder à la branche du projet](https://github.com/Liily77/lydianeghad.github.io/tree/Analyse-Donn%C3%A9es-Sportives)

**Objectifs principaux :**  

◾ **Préparation des données** : Extraction et nettoyage des données **JSON**, transformation pour obtenir des **informations par rameur et par segment**.  
◾ **Analyse exploratoire** : Calculs des **vitesses moyennes, cadences, calories consommées par kilomètre**.  
◾ **Comparaison des rameurs** : Étude des **stratégies adoptées** et des **différences de performances**.  
◾ **Visualisation dynamique** : Graphiques interactifs montrant **l'évolution des performances** sur la course.  
◾ **Corrélations avancées** : Analyse de l'impact de la **cadence sur la dépense énergétique** et la **vitesse finale**.

**🛠️ Technologies :** Python, Pandas, Matplotlib, Seaborn, Plotly, Jupyter

<p align="center">
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" alt="Python" width="60" height="60" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/pandas/pandas-original-wordmark.svg" alt="Pandas" width="60" height="60" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/matplotlib/matplotlib-original.svg" alt="Matplotlib" width="60" height="60" />
  <img src="https://seaborn.pydata.org/_images/logo-tall-lightbg.svg" alt="Seaborn" width="60" height="60" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/plotly/plotly-original.svg" alt="Plotly" width="60" height="60" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/jupyter/jupyter-original.svg" alt="Jupyter" width="60" height="60" />
</p>

<hr>

<h2 align="center">👩🏻‍💻 Mes projets dans le développement web</h2>
<br>

<h3>🔹 Projet : <strong>Création d'un Tutoriel HTML/CSS 👩🏻‍💻</strong></h3>

👉 Voir le site ici : <a href="https://lydianeghad.alwaysdata.net/duweb24/CSS/TP3/Template.html"> Site Tutoriel</a> 

<p><strong>Description :</strong><br>
Ce projet est un tutoriel interactif conçu pour enseigner les bases du développement front-end en HTML et CSS.</p>
<p><a href="https://github.com/Liily77/lydianeghad.github.io/tree/projet_tutoriel">Accéder à la branche du projet</a></p>
<p align="center">
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/html5/html5-original.svg" alt="HTML5" width="60" height="60" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/css3/css3-original.svg" alt="CSS3" width="60" height="60" />
</p>

<hr>

<h3>🔹 Projet: <strong>Clinique Oscar - Prise de Rendez-vous Ostéopathie ⚕️</strong></h3>

👉 Voir le site ici : <a href="https://lydianeghad.alwaysdata.net/Clinique_Oscar/"> Site Clinique Oscar</a> 

<p><strong>Description :</strong><br>
Un site web de prise de rendez-vous pour une clinique d'ostéopathie.</p>
<p><a href="https://github.com/Liily77/lydianeghad.github.io/tree/projet_clinique_oscar">Accéder à la branche du projet</a></p>
<p align="center">
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/html5/html5-original.svg" alt="HTML5" width="60" height="60" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/css3/css3-original.svg" alt="CSS3" width="60" height="60" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/javascript/javascript-original.svg" alt="JavaScript" width="60" height="60" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/php/php-original.svg" alt="PHP" width="60" height="60" />
</p>

<hr>

<h3>🔹 Projet : <strong>Carnet de Suivi d'Expérience de Conduite 🚗</strong></h3>

👉 Voir le site ici : <a href="https://lydianeghad.alwaysdata.net/SPConduite/index.html"> SP Conduite</a>

<p><strong>Description :</strong><br>
Ce projet permet aux utilisateurs de suivre leurs expériences de conduite en enregistrant des détails comme la météo, le trafic, et la distance parcourue.</p>
<p><a href="https://github.com/Liily77/lydianeghad.github.io/tree/projet_SP_conduite">Accéder à la branche du projet</a></p>
<p align="center">
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/html5/html5-original.svg" alt="HTML5" width="60" height="60" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/css3/css3-original.svg" alt="CSS3" width="60" height="60" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/javascript/javascript-original.svg" alt="JavaScript" width="60" height="60" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/mysql/mysql-original.svg" alt="MySQL" width="60" height="60" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/php/php-original.svg" alt="PHP" width="60" height="60" />
  <img src="https://www.phpmyadmin.net/static/images/logo-og.png" alt="phpMyAdmin" width="60" height="60" />
  <img src="https://img.icons8.com/fluency/344/database.png" alt="LocalStorage" width="60" height="60" />
</p>
