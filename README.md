<h1>Projet Clinique Oscar/CSS</h1>

👉 Voir le site ici : <a href="https://lydianeghad.alwaysdata.net/Clinique_Oscar/"> Site Clinique Oscar</a>

<h2>Description 🖋️</h2>

Le projet Clinique Oscar est un site de prise de rendez-vous en ligne pour une clinique d'ostéopathie. 
Ce projet permet aux utilisateurs de réserver des consultations ostéopathiques, en fournissant leurs informations de contact et en sélectionnant une date et un tarif via un formulaire interactif. 
L'idée principale est d'offrir une plateforme simple, ergonomique et responsive pour faciliter la gestion des consultations.

Les utilisateurs peuvent choisir différents tarifs selon leur situation (étudiants, adultes ou tarifs pour plusieurs séances), 
et un système de validation des informations est mis en place pour assurer la cohérence des données fournies.

<h2> Fonctionnalités principales 💡</h2>
<li><b>Système de prise de rendez-vous</b> :  Le formulaire permet de réserver une consultation en fournissant des informations personnelles. 
Les utilisateurs peuvent choisir une date via un calendrier interactif (Flatpickr) et un horaire pour leur rendez-vous</li>
<li><b>Validation des formulaires</b> : Les champs du formulaire (nom, téléphone, courriel) sont soumis à une validation stricte (regex pour les numéros de téléphone et courriels) 
pour s'assurer que les données sont valides avant l'envoi </li>
<li><b>Tarifs flexibles</b> : Les utilisateurs peuvent choisir parmi plusieurs options tarifaires adaptées à leur profil (étudiants, adultes ou tarif spécial pour 6 séances) </li>
<li><b>Calendrier interactif</b> : Le sélecteur de date empêche les réservations les week-ends (samedi et dimanche) et propose uniquement des rendez-vous les jours de semaine. </li>

<h2>Technologies utilisées 💻</h2>

<li><b>HTML5</b> : Structure de base de la page web.</li>
<li><b>CSS3</b> : Pour le style et la mise en page responsive, avec plusieurs media queries pour s'adapter aux différents appareils (mobile, tablette, desktop).</li>
<li><b>Flatpickr</b> : Bibliothèque JavaScript utilisée pour la sélection de la date, avec des options personnalisées pour limiter les jours sélectionnables.</li>
<li><b>JavaScript Vanilla</b> : Utilisé pour ajouter des fonctionnalités comme la sélection d'horaire dynamique et l'intégration de Flatpickr.</li>
<li><b>PHP</b> : Traitement des données du formulaire et gestion des rendez-vous (le fichier PHP doit encore être implémenté côté serveur).</li>

