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


<h2>Compétences acquises ✔️</h2>

<li><b>Gestion de formulaires interactifs</b> : J'ai appris à créer et valider des formulaires complexes avec des champs variés (texte, email, date, sélection multiple) et à utiliser des expressions 
régulières pour vérifier les données saisies.</li>
<li><b>Utilisation de bibliothèques JavaScript</b>: J'ai approfondi mes compétences en JavaScript en intégrant la bibliothèque Flatpickr pour gérer la sélection de dates avec des options personnalisées.</li>
<li><b>Responsive Design</b> : J'ai amélioré mes compétences en CSS pour rendre le site responsive sur différents appareils (mobile, tablette, desktop), en utilisant les media queries.</li>
<li><b>Validation des formulaires avec JavaScript et PHP</b> : Ce projet m'a permis de comprendre l'importance de la validation côté client (JavaScript) et côté serveur (PHP).</li>
<li><b>Expérience utilisateur (UX)</b> : J'ai travaillé sur l'amélioration de l'expérience utilisateur en optimisant l'ergonomie du formulaire et la navigation sur le site.</li>
<li><b></b></li>


<h2>Ce que j'ai appris 💪</h2>
<li><b>Mise en place d'un calendrier interactif avec Flatpickr</b>: J'ai découvert comment intégrer et configurer la bibliothèque Flatpickr pour offrir aux utilisateurs une interface fluide de sélection de dates, tout en imposant des restrictions (jours ouvrables uniquement).</li>
<li><b>Validation avancée des formulaires</b> : J'ai renforcé mes compétences en validation de données en utilisant des expressions régulières pour vérifier des champs tels que les numéros de téléphone et les adresses e-mail, garantissant ainsi l'intégrité des informations saisies par les utilisateurs.</li>
<li><b>Gestion des interactions utilisateur avec JavaScript</b> : J'ai appris à gérer les événements utilisateur, comme le changement d'horaires dynamiques en fonction de la sélection de date, rendant le formulaire plus interactif et intuitif.</li>
<li><b>Adaptation du design pour différentes tailles d'écran</b> : J'ai approfondi mes compétences en responsive design, en particulier pour la gestion des formulaires sur mobile, en veillant à ce que chaque élément soit
ergonomique et lisible sur des écrans plus petits </li>
<li><b>Création d'une expérience utilisateur intuitive</b> : Ce projet m'a permis d'améliorer ma capacité à concevoir des interfaces simples et fonctionnelles, en tenant compte des besoins des utilisateurs lors de la prise de rendez-vous.</li>

<h2>Difficultés rencontrées et solutions 🎯</h2>
<li><b>Mise en place du calendrier avec Flatpickr</b> : J'ai rencontré des difficultés à configurer correctement le calendrier pour exclure les week-ends et limiter les dates. La solution est passée par l'utilisation des options disable et minDate de Flatpickr.</li>
<li><b>Validation des formulaires</b> : Valider les numéros de téléphone et courriels via regex a posé des défis. J'ai ajusté les expressions régulières pour garantir la validité des données saisies.</li>
<li><b>Gestion des horaires dynamiques</b> : Intégrer la génération dynamique des horaires en fonction de la date a été complexe. J'ai utilisé JavaScript pour ajuster les créneaux disponibles en fonction des jours ouvrables.</li>
<li><b>Structure du formulaire</b> : Assurer l'ergonomie du formulaire avec plusieurs champs a nécessité une réorganisation via Flexbox pour garantir une mise en page fluide.</li>
