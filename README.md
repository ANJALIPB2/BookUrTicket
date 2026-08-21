# 🎟️ BookUrTicket — Movie Ticket Booking Platform

BookUrTicket is a full-stack movie ticket booking web application built with **Python, Flask, SQLite, HTML, CSS, and JavaScript**.

The application allows users to explore movies, watch trailers, select seats, add snacks, complete a simulated checkout process, and generate digital movie tickets.

It also includes an administrator dashboard for managing movies, bookings, users, and basic platform statistics.

---

## ✨ Features

### 👤 User Features

- 🔐 User registration and login
- 🎬 Browse available movies
- 🔎 Search for movies
- 🎭 Filter movies by genre
- 🌐 Browse movies by language
- 🔥 View trending movies
- ▶️ Watch movie trailers
- 💺 Select available seats
- 🪑 Different seat categories:
  - Classic
  - Prime
  - Recliner
- 🍿 Add snacks and beverages to bookings
- 💳 Simulated payment/checkout flow
- 🎟️ Generate digital movie tickets
- 📄 Download tickets as PDF
- 📱 Share booking information through WhatsApp
- ❤️ Add movies to favorites
- 📋 View booking history
- 👤 Manage user profile
- 🌓 Dark/light theme support
- 📱 Responsive user interface

---

## 👑 Admin Features

The application includes an administrator dashboard with features for managing the platform.

### Dashboard

- View total users
- View total bookings
- View revenue statistics
- Monitor booking information

### Movie Management

Administrators can:

- Add movies
- Add movie posters
- Add movie descriptions
- Add showtimes
- Manage movie information

### Booking Management

Administrators can:

- View customer bookings
- View booking details
- Monitor transaction information

---

## 🛠️ Technology Stack

| Category | Technology |
|----------|------------|
| Frontend | HTML5, CSS3, JavaScript |
| Backend | Python, Flask |
| Database | SQLite3 |
| PDF Generation | xhtml2pdf |
| Client-side PDF | html2pdf.js |
| Email | SMTP |
| Styling | Custom CSS |
| Fonts | Google Fonts |

---

## 📂 Project Structure

```text
BookUrTicket/
│
├── app.py
├── database.py
├── email_service.py
├── requirements.txt
├── movies.json
│
├── templates/
│   ├── index.html
│   ├── home.html
│   ├── navbar.html
│   ├── profile.html
│   ├── cinemas.html
│   ├── ticket_view.html
│   └── admin.html
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
└── tickets/
    └── Generated ticket files
