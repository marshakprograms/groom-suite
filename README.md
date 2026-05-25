# Ronald's Groom Suite 💈

Ronald’s Groom Suite is a full-stack business operations and booking platform built for a luxury mobile barber service specializing in weddings and group grooming experiences across the Triangle area of North Carolina.

The platform was designed to streamline client onboarding, appointment management, groom party coordination, communication workflows, and administrative scheduling through a modern responsive web application.

Built with Flask and SQLAlchemy, the system combines customer-facing luxury branding with operational workflow tools typically found in larger booking and service management platforms.

The project was designed to balance premium customer experience with operational efficiency for a real-world mobile service business.

---

## 🌐 Live Demo

> Coming soon — deploying to Railway

---

## 📸 Screenshots

> Screenshots coming after deployment

---

## 🔧 Key Technical Highlights

- Full-stack Flask web application architecture
- Role-based authentication and authorization
- Dynamic booking workflow management
- Responsive mobile-first interface design
- Real-time-style messaging and notification system
- Admin scheduling and conflict detection tools
- Stripe payment integration foundation
- Environment-based configuration management
- Modular SQLAlchemy data modeling
- Business workflow automation for service operations

---

## ✨ Features

### Public Site

- Luxury branded homepage with hero images and service details
- Feature pages:
  - We Come to You
  - Premium Experience
  - Professional Results
  - Groom Squad Ready
- Mobile responsive design optimized for phones and tablets
- Inquiry and booking form with validation

### Groom Portal

- Secure login with forced password change
- Booking status dashboard
- Party member management
- Booking detail editing
- In-app messaging
- Booking cancellation workflow
- Unread message notification alerts

### Admin Dashboard

- Booking approval and management
- Scheduling conflict detection
- Admin calendar system
- In-app client messaging
- Booking detail management

### Notifications

- Automated email-to-SMS notifications
- Booking cancellation alerts
- New booking request notifications

### Security

- Flask-Login authentication
- Role-based access control
- Password reset workflow
- Temporary password generation

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask, SQLAlchemy |
| Authentication | Flask-Login, Werkzeug |
| Database | SQLite (development), PostgreSQL (planned) |
| Email/SMS | Flask-Mail, email-to-SMS gateway |
| Frontend | Jinja2, HTML, CSS |
| Hosting | Railway deployment pipeline |
| Version Control | Git, GitHub |

---

## 🚀 Local Setup

### Installation

```bash
git clone https://github.com/MarshaKDesigns-Dev/groom-suite.git

cd groom-suite

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt

py app.py
```

---

## 🔐 Environment Variables

Create a `.env` file:

```env
SECRET_KEY=your-secret-key
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
BARBER_PHONE=9191234567@vtext.com
BARBER_EMAIL=admin@groomsuite.com
```

---

## 🚀 Planned Enhancements

- [ ] Railway deployment with PostgreSQL
- [ ] Google Calendar integration
- [ ] Stripe payment workflow
- [ ] Twilio SMS integration
- [ ] Push notifications
- [ ] Multi-barber support

---

## 👩🏽‍💻 Author

**Marsha K. Shearin**  
Founder of MarshaKDesigns  
Business Operations & Platform Developer  
Durham, NC

GitHub: [@MarshaKDesigns-Dev](https://github.com/MarshaKDesigns-Dev)

---

## 📄 License

Built for Ronald's Unisex Barbershop in Durham, North Carolina.

All rights reserved.