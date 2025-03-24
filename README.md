# Project: Clinique Oscar - Osteopathy Appointment Scheduling 🩺📅

👉 View the website here: [Clinique Oscar](https://lydianeghad.alwaysdata.net/Clinique_Oscar/)

## Description 🖋️

The Clinique Oscar project is an online appointment booking site for an osteopathy clinic. Users can book osteopathic consultations by providing their contact information and selecting a date and rate through an interactive form. The main idea is to offer a simple, ergonomic, and responsive platform to facilitate appointment management.

Users can select different rates according to their situation (students, adults, or multiple-session packages). A robust validation system ensures the consistency and correctness of the provided data.

## Main Features 💡

- **Appointment Booking System:** Users can book appointments by entering personal information. They can choose a date via an interactive calendar (Flatpickr) and select a time slot.
- **Form Validation:** Form fields (name, phone number, email) are rigorously validated using regex patterns to ensure data accuracy before submission.
- **Flexible Pricing:** Users can choose from multiple pricing options tailored to their profile (students, adults, or a special rate for six sessions).
- **Interactive Calendar:** The date picker restricts weekend bookings (Saturday and Sunday) and only offers weekday appointments.

## Technologies Used 💻

- **HTML5:** Fundamental webpage structure.
- **CSS3:** Responsive styling and layout, employing media queries for compatibility across various devices (mobile, tablet, desktop).
- **Flatpickr:** JavaScript library used for date selection, with customized options to limit selectable days.
- **Vanilla JavaScript:** Provides dynamic functionalities like dynamic time slot selection and Flatpickr integration.
- **PHP:** Form data processing and appointment management (server-side PHP implementation pending).
