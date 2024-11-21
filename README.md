<h1>Projet : Analyse des performances des rameurs sur 2000m 🏅</h1>

👉 Voir le notebook ici : <a href="https://github.com/Liily77/lydianeghad.github.io/blob/analyse-donn%C3%A9es-sportives/analyse-rameurs.ipynb"> Notebook</a>
<ul>
  <li><b>Exemples de visualisations :</b>
    <ul>
      <li>Boxplot des vitesses par sexe.</li>
      <li>Corrélations cadence-calories.</li>
      <li>Régressions calories-temps.</li>
      <li>Carte thermique des efforts par split.</li>
      <li>Progression dynamique des vitesses.</li>
    </ul>
  </li>
</ul>

<h2>Description 🖋️</h2>

Ce projet Python a pour objectif d'analyser les performances des rameurs sur une distance de 2000m en utilisant des données segmentées par portions de 500m. À travers plusieurs visualisations interactives et statiques, nous avons exploré les facteurs influençant la performance et comparé les rameurs entre eux. Ce projet met également en évidence des analyses avancées comme les corrélations entre cadence et calories, ou encore la comparaison des performances avec des champions mondiaux.
Ce projet a été réalisé en collaboration avec plusieurs coéquipiers dans le cadre de nos études. 
<h2>Structure du projet 💡</h2>
Le projet est structuré autour de plusieurs étapes :
<li><b>Préparation des données</b> : Extraction et nettoyage des données au format JSON, transformation des données pour obtenir des informations par participants et segments.</li>
<li><b>Analyses exploratoires</b> : Calculs des vitesses moyennes, des cadences, et des calories consommées par kilomètre. Ajout de catégories comme le sexe et les stratégies adoptées par les rameurs.</li>
<li><b>Visualisations principales</b> : Graphiques comparant les performances des rameurs, leur progression et les corrélations entre les variables.</li>

<h2>Technologies utilisées 💻</h2>
<ul>
<li><b>Python</b> : Langage principal utilisé pour l'analyse et le traitement des données.</li> 
<li><b>Pandas</b> : Pour manipuler et nettoyer les données, avec des DataFrames facilitant les analyses complexes.</li>
<li><b>Matplotlib</b> : Pour la création de visualisations statiques, comme les graphiques en ligne ou en barres.</li> 
<li><b>Seaborn</b> : Utilisé pour générer des graphiques avancés et analytiques grâce à des thèmes et des fonctionnalités riches.</li> 
<li><b>Plotly</b> : Pour des visualisations interactives et dynamiques, comme des animations et des graphiques interactifs.</li> 
<li><b>Jupyter Notebook</b> : Environnement de développement utilisé pour coder, visualiser, et documenter le projet de manière claire et interactive.</li> 
</ul>


<h2>Compétences acquises ✔️</h2>
<li><b>Manipulation de données avec Pandas</b> : Analyse, transformation et visualisation des données.</li>
<li><b>Création de visualisations dynamiques</b> : Utilisation de Plotly pour des graphiques interactifs (barres, cartes thermiques, régressions).</li>
<li><b>Statistiques et corrélations</b> : Calculs avancés comme la corrélation entre cadence et calories consommées.</li>
<li><b>Storytelling avec les données</b> : Présentation claire et visuelle des analyses pour faciliter l'interprétation.</li>

<h2>Ce que j'ai appris 💪</h2>
<li><b>Nettoyage et transformation des données</b> : Traitement de données complexes au format JSON pour les rendre exploitables.</li>
<li><b>Visualisation avancée</b> : Maîtrise de bibliothèques comme Plotly, Seaborn et Matplotlib.</li>
<li><b>Analyse critique des données</b> : Identifier des patterns de performance et des facteurs influençant les résultats des rameurs.</li>
<li><b>Création d'animations interactives</b> : Animation des graphiques pour représenter l'évolution des performances sur 2000m.</li>

<h2>Difficultés rencontrées et solutions 🎯</h2>
<li><b>Données JSON imbriquées</b> : Les données étaient complexes à manipuler. <b>Solution</b> : Utilisation de <code>pd.json_normalize</code> pour extraire efficacement les informations.</li>
<li><b>Visualisations interactives</b> : Créer des graphiques dynamiques adaptés à des métriques variées. <b>Solution</b> : Expérimentation avec Plotly pour des visualisations intuitives.</li>
<li><b>Corrélation des variables</b> : Analyser des relations non linéaires entre calories et temps. <b>Solution</b> : Utiliser des régressions linéaires et des cartes thermiques pour mieux interpréter les résultats.</li>


