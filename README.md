# Project: Driving Experience Logbook 🚗📔

👉 View the website here: [SP Conduite](https://lydianeghad.alwaysdata.net/SPConduite/index.html)

## Description 🖋️

This project is a digital logbook designed to record and analyze driving experiences. Users can add detailed information about their trips, including weather conditions, traffic, maneuvers performed, and an overall evaluation of their experience. Through an intuitive interface, users can track their progress and view statistics about their trips, such as total distance traveled and duration.

## Main Features 🛠️

- **Adding Driving Experiences:** Users can input information about the date, start and end times, distance traveled, and other details via an interactive form.
- **Progress Tracking:** A table displays all recorded experiences, including details of each trip.
- **Dynamic Statistics:** Automatic calculation of average distance, total trip duration, and progress percentage toward a 3000 km goal.
- **Form Validation:** Data entries are strictly validated, with error messages provided for incorrect inputs.
- **Data Management with MySQL:** The project uses phpMyAdmin and MySQL to manage trip data. Information entered through the form is saved in a database and can be reviewed later.
- **Data Reset:** Option to reset the logbook and delete local data to start anew.

## Technologies Used 💻

- **HTML5:** Page structure with sections dedicated to adding experiences, progress, and statistics.
- **CSS3:** Responsive styling and layout, including media queries to ensure a great mobile user experience.
- **JavaScript (Vanilla):** Used for dynamic functionalities such as event handling, form validation, updating localStorage, and calculating statistics.
- **LocalStorage:** Temporarily storing experience data before permanent database entry.
- **MySQL & phpMyAdmin:** Used to manage driving experience data on a server. phpMyAdmin provides easy access and modification of the database through an intuitive web interface.
