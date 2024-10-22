<h1>Projet : Carnet de Suivi d'Expérience de Conduite</h1>

👉 Voir le site ici : <a href="https://lydianeghad.alwaysdata.net/SPConduite/index.html"> SP Conduite</a>

<h2>Description 🖋️</h2>

Le projet est un carnet de suivi numérique conçu pour enregistrer et analyser les expériences de conduite. 
Il permet aux utilisateurs d'ajouter des informations détaillées sur leurs trajets, telles que la météo, le trafic, les manœuvres effectuées et l'appréciation globale de l'expérience. 
Grâce à une interface intuitive, les utilisateurs peuvent suivre leur progression et consulter des statistiques sur leurs trajets, comme la distance totale parcourue et la durée des trajets.

<h2>Fonctionnalités principales 🛠️</h2>

<li><b>Ajout d'une expérience de conduite</b> : Les utilisateurs peuvent saisir des informations sur la date, l'heure de départ et d'arrivée, la distance parcourue, et d'autres détails via un formulaire interactif.</li>
<li><b>Suivi de la progression</b> : Un tableau affiche toutes les expériences enregistrées, incluant les détails de chaque trajet.</li>
<li><b>Statistiques dynamiques</b> : Calcul automatique de la distance moyenne, de la durée totale des trajets, et affichage du pourcentage de progression vers un objectif de 3000 km.</li>
<li><b>Validation du formulaire</b> : Les données sont soumises à une validation stricte, avec des messages d'erreurs en cas de saisie incorrecte.</li>
<li><b>Gestion des données avec MySQL</b> : Le projet utilise phpMyAdmin et MySQL pour gérer les données des trajets. Les informations saisies dans le formulaire sont enregistrées dans une base de données et peuvent être consultées ultérieurement.</li>
<li><b>Réinitialisation des données </b> : Possibilité de réinitialiser le carnet et de supprimer les données locales pour recommencer à zéro.</li>


<h2>Technologies utilisées 💻</h2>

<li><b>HTML5</b> : Structure de la page, avec des sections dédiées à l'ajout d'expériences, à la progression et aux statistiques.</li>
<li><b>CSS3</b> : Pour le style et la mise en page responsive, avec des media queries pour garantir une bonne expérience utilisateur sur mobile.</li>
<li><b>JavaScript (Vanilla)</b> : Utilisé pour les fonctionnalités dynamiques comme la gestion des événements, la validation des formulaires, la mise à jour du localStorage et le calcul des statistiques.</li>
<li><b>LocalStorage</b> : Pour stocker temporairement les données des expériences avant leur enregistrement définitif en base de données.</li>
<li><b>MySQL & phpMyAdmin</b> Utilisés pour gérer les données des expériences de conduite sur un serveur.
Grâce à phpMyAdmin, la base de données est facilement accessible et modifiable via une interface web intuitive.</li>

<h2>Compétences acquises ✔️</h2>

<li><b>Manipulation du DOM</b> : Ajout dynamique d'éléments HTML avec JavaScript, comme les options des listes déroulantes et les lignes de tableaux.</li>
<li><b>Gestion du LocalStorage et MySQL</b></li> : J'ai appris à gérer le stockage local des données avant de les insérer dans une base de données MySQL, tout en assurant leur récupération via phpMyAdmin.</li>
<li><b>Validation de formulaires</b> : J'ai mis en place une validation robuste pour garantir la cohérence des données avant leur enregistrement.</li>
<li><b>Calculs statistiques dynamiques</b> : Calculs automatisés pour afficher la distance moyenne, la durée totale et l'avancement par rapport à un objectif défini.</li>
<li><b>Conception responsive</b> : J'ai veillé à ce que le site soit utilisable sur toutes les tailles d'écran (mobile, tablette, desktop).</li>

<h2>Ce que j'ai appris 💪</h2>
<li><b>Validation de données et stockage en base</b> : J'ai appris à valider des données complexes (dates, heures, distances) avant de les enregistrer dans une base de données MySQL, tout en gérant les erreurs utilisateur avec des messages d'avertissement clairs.</li>
<li><b>Intégration de MySQL avec phpMyAdmin</b> : L'utilisation de phpMyAdmin m'a permis de gérer facilement les tables, d'exécuter des requêtes SQL, et de maintenir une base de données structurée.</li>
<li><b>Gestion des événements</b></li> : J'ai approfondi la gestion des événements en JavaScript, en particulier pour des actions comme la validation des formulaires et la mise à jour dynamique du contenu.</li>
<li><b>Optimisation de l'UX</b> : J'ai appris à structurer des formulaires et à guider l'utilisateur via des messages d'erreur clairs, garantissant ainsi une expérience utilisateur fluide et intuitive.</li>

<h2>Difficultés rencontrées et solutions 🎯</h2>
<li><b>Validation des dates et heures</b> : Vérifier que l'heure d'arrivée est postérieure à l'heure de départ a été un défi. J'ai utilisé une conversion des heures en minutes pour faciliter la comparaison.</li>
<li><b>Synchronisation avec MySQL</b> : L'intégration des données locales stockées dans le LocalStorage avec MySQL a demandé une bonne gestion des requêtes SQL pour éviter les doublons et garantir la cohérence des informations.</li>
<li><b>Affichage dynamique des données</b> : Insérer des données dans le tableau de progression tout en conservant un format cohérent s'est avéré difficile. J'ai résolu cela en créant une fonction de formatage des dates et en optimisant le remplissage du tableau avec des boucles.</li>
