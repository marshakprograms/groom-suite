# Ronald's Groom Suite 💈

**A full-stack Flask booking and client portal application for a mobile luxury wedding grooming service.**

Built for Ronald's Unisex Barbershop (Durham, NC) — a mobile barber who brings a fully equipped Sprinter van to wedding venues across the Triangle area.

---

## 🌐 Live Demo

> Coming soon — deploying to Railway

---

## 📸 Screenshots

> Screenshots coming after deployment

---

## ✨ Features

### Public Site
- Luxury branded homepage with hero images and service details
- Feature pages: We Come to You, Premium Experience, Professional Results, Groom Squad Ready
- Mobile responsive design — works on all phones and tablets
- Inquiry/booking form with full validation (email confirmation, date restriction, party size)

### Groom Portal
- Secure login with forced password change on first access
- Booking status dashboard (Pending, Confirmed, Rejected, Cancelled)
- Party member management — add/remove members with roles and services
- Preferred appointment time selection
- Edit booking details — date, venue, party size, add-ons
- In-app messaging with the barber
- Cancel booking with in-app confirmation
- Unread message badge with blinking alert

### Admin Dashboard
- View, confirm, reject, and cancel bookings
- Scheduling conflict detection and highlighting
- Admin calendar with upcoming events
- In-app messaging with each groom
- Unread message notifications
- Booking detail view with full party member list

### Notifications
- Automated email-to-SMS notification to barber on new inquiry
- Automated SMS notification on booking cancellation
- New date request notification after rejection

### Security
- Flask-Login authentication
- Role-based access control (admin vs client)
- Forced password change on first login
- Temporary password generation on registration
- Forgot password flow with email reset

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask, SQLAlchemy |
| Auth | Flask-Login, Werkzeug |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Email/SMS | Flask-Mail, email-to-SMS gateway |
| Frontend | Jinja2, HTML, CSS (custom black & gold design) |
| Fonts | Cormorant Garamond, Montserrat (Google Fonts) |
| Hosting | Railway (pending) |
| Version Control | Git, GitHub |

---

## 🚀 Local Setup

### Prerequisites
- Python 3.10+
- pip
- Git

### Installation

```bash
# Clone the repo
git clone https://github.com/marshakprograms/groom-suite.git
cd groom-suite

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Fill in your values

# Run the app
py app.py
```

### Environment Variables

Create a `.env` file with the following:

```
SECRET_KEY=your-secret-key
MAIL_USERNAME=your-gmail@gmail.com
MAIL_PASSWORD=your-gmail-app-password
BARBER_PHONE=9191234567@vtext.com
BARBER_EMAIL=admin@groomsuite.com
```

### Seed the Database

```bash
py seed.py
```

---

## 🔑 Demo Credentials

| Role | Email | Password |
|---|---|---|
| Admin (Barber) | admin@groomsuite.com | admin123 |
| Client (Groom) | *(submit an inquiry to create)* | *(temp password shown on screen)* |

---

## 📁 Project Structure

```
groom-suite/
├── app.py              # App factory, config, template filters
├── auth.py             # Login, logout, register routes
├── routes.py           # All app routes (portal, admin, messaging)
├── models.py           # SQLAlchemy models (User, Booking, PartyMember, Message)
├── config.py           # Configuration from .env
├── seed.py             # Database seeder
├── requirements.txt    # Python dependencies
├── static/
│   └── css/
│       └── style.css   # Custom black & gold design system
└── templates/
    ├── base.html
    ├── index.html
    ├── inquiry.html
    ├── portal.html
    ├── messages.html
    ├── login.html
    ├── change_password.html
    ├── forgot_password.html
    ├── about.html
    ├── edit_booking.html
    ├── features/
    │   ├── we_come_to_you.html
    │   ├── premium_experience.html
    │   ├── professional_results.html
    │   └── groom_squad_ready.html
    └── admin/
        ├── dashboard.html
        ├── booking_detail.html
        ├── calendar.html
        └── messages.html
```

---

## 🔮 Future Improvements

- [ ] Railway deployment with PostgreSQL
- [ ] Custom domain (ronaldsgroomsuite.com)
- [ ] Email verification on registration
- [ ] Google Calendar integration for barber
- [ ] Stripe payment integration for deposits
- [ ] SMS via Twilio (currently email-to-SMS gateway)
- [ ] Push notifications for mobile
- [ ] Review/testimonial system
- [ ] Multi-barber support

---

## 👩🏽‍💻 Author

**Marsha K. Shearin**
Freelance Full-Stack Developer — Durham, NC
GitHub: [@marshakprograms](https://github.com/marshakprograms)

---

## 📄 License

This project was built for Ronald's Unisex Barbershop, Durham NC.
All rights reserved.

---

*Built with Flask, deployed with Railway, designed with love in Durham, NC 💈*