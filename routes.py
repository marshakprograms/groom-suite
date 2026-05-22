from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, User, Booking, PartyMember, Message
from functools import wraps
from flask_mail import Message as MailMessage
from flask import current_app
import random
import string
import stripe


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            return redirect(url_for("index"))
        return f(*args, **kwargs)

    return decorated_function


def register_routes(app, mail):

    @app.route("/admin")
    @login_required
    @admin_required
    def admin_dashboard():
        bookings = Booking.query.order_by(Booking.wedding_date).all()
        total = len(bookings)
        pending = len([b for b in bookings if b.status == "pending"])
        confirmed = len([b for b in bookings if b.status == "confirmed"])
        from collections import Counter

        date_counts = Counter(b.wedding_date for b in bookings)
        conflict_dates = {date for date, count in date_counts.items() if count > 1}
        return render_template(
            "admin/dashboard.html",
            bookings=bookings,
            total=total,
            pending=pending,
            confirmed=confirmed,
            conflict_dates=conflict_dates,
        )

    @app.route("/admin/booking/<int:id>/confirm")
    @login_required
    @admin_required
    def confirm_booking(id):
        booking = Booking.query.get_or_404(id)
        booking.status = "confirmed"
        db.session.commit()
        flash("Booking confirmed.")
        return redirect(url_for("admin_dashboard"))

    @app.route("/admin/booking/<int:id>/reject")
    @login_required
    @admin_required
    def reject_booking(id):
        booking = Booking.query.get_or_404(id)
        booking.status = "rejected"
        db.session.commit()
        flash("Booking rejected.")
        return redirect(url_for("admin_dashboard"))

    @app.route("/portal")
    @login_required
    def portal():
        if current_user.role == "admin":
            return redirect(url_for("admin_dashboard"))
        booking = Booking.query.filter_by(user_id=current_user.id).first()
        added = request.args.get("added")
        return render_template("portal.html", booking=booking, added=added)

    @app.route("/portal/add-member", methods=["POST"])
    @login_required
    def add_member():
        booking = Booking.query.filter_by(user_id=current_user.id).first()
        if booking:
            current_count = len(booking.party_members)
            if current_count >= booking.party_size:
                flash(
                    f"ALERT: You have reached your maximum party size of {booking.party_size} members.  To add more, please edit your booking to increase your party size."
                )
                return redirect(url_for("portal"))
            name = request.form.get("member_name")
            if name:
                role = request.form.get("member_role", "Groomsman")
                member = PartyMember(
                    name=name, role=role, service="Full Service", booking_id=booking.id
                )
                db.session.add(member)
                db.session.commit()
                return redirect(url_for("portal", added=name))
        return redirect(url_for("portal"))

    @app.route("/portal/remove-member/<int:id>")
    @login_required
    def remove_member(id):
        member = PartyMember.query.get_or_404(id)
        db.session.delete(member)
        db.session.commit()
        flash("Party member removed.")
        return redirect(url_for("portal"))

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/inquiry", methods=["GET", "POST"])
    def inquiry():
        if request.method == "POST":
            name = request.form.get("name")
            email = request.form.get("email")
            phone = request.form.get("phone")
            wedding_date = request.form.get("wedding_date")
            start_time = request.form.get("start_time")
            venue = request.form.get("venue")
            party_size_int = int(request.form.get("party_size"))
            if party_size_int == 1:
                package = "Groom Only"
            elif party_size_int <= 4:
                package = "Small Group Package"
            elif party_size_int <= 8:
                package = "Full Squad Package"
            else:
                package = "Large Party Package"
            addons = request.form.get("addons")
            notes = request.form.get("notes")

            existing_user = User.query.filter_by(email=email).first()
            if not existing_user:
                from werkzeug.security import generate_password_hash

                temp_password = "".join(
                    random.choices(string.ascii_letters + string.digits, k=8)
                )
                new_user = User(
                    name=name,
                    email=email,
                    phone=phone,
                    password=generate_password_hash(temp_password),
                    role="client",
                )
                db.session.add(new_user)
                db.session.flush()
                user_id = new_user.id
                try:
                    msg = MailMessage(
                        subject="New Booking Inquiry — Groom Suite",
                        sender=current_app.config["MAIL_USERNAME"],
                        recipients=[current_app.config["BARBER_PHONE"]],
                    )
                    msg.body = f"New inquiry from {name} for {wedding_date} at {venue}. Log in to review: http://127.0.0.1:5000/admin"
                    mail.send(msg)
                except Exception as e:
                    print(f"SMS notification failed: {e}")
                flash(
                    f"Welcome, {name}! Your inquiry has been submitted. Log in with your email and temporary password: <strong>{temp_password}</strong>"
                )
            else:
                user_id = existing_user.id
                flash(f"Welcome back, {name}! Your new inquiry has been submitted.")

            booking = Booking(
                wedding_date=wedding_date,
                venue=venue,
                start_time=start_time,
                party_size=party_size_int,
                package=package,
                addons=addons,
                notes=notes,
                status="pending",
                user_id=user_id,
            )
            db.session.add(booking)
            db.session.commit()
            return redirect(url_for("login"))

        return render_template("inquiry.html")

    @app.route("/about")
    def about():
        return render_template("about.html")

    @app.route("/change-password", methods=["GET", "POST"])
    @login_required
    def change_password():
        if request.method == "POST":
            from werkzeug.security import generate_password_hash

            new_password = request.form.get("new_password")
            confirm = request.form.get("confirm_password")
            if new_password != confirm:
                flash("Passwords do not match.")
                return redirect(url_for("change_password"))
            current_user.password = generate_password_hash(new_password)
            current_user.password_changed = True
            db.session.commit()
            flash("Password updated successfully!")
            return redirect(url_for("portal"))
        return render_template("change_password.html")

    @app.route("/admin/booking/<int:id>")
    @login_required
    @admin_required
    def booking_detail(id):
        booking = Booking.query.get_or_404(id)
        return render_template("admin/booking_detail.html", booking=booking)

    @app.route("/portal/edit", methods=["GET", "POST"])
    @login_required
    def edit_booking():
        booking = Booking.query.filter_by(user_id=current_user.id).first()
        if not booking:
            return redirect(url_for("portal"))
        if request.method == "POST":
            old_date = booking.wedding_date
            new_date = request.form.get("wedding_date")
            booking.wedding_date = new_date
            booking.venue = request.form.get('venue')
            booking.start_time = request.form.get('start_time')
            booking.party_size = int(request.form.get('party_size'))
            booking.notes = request.form.get('notes')
            current_user.name = request.form.get('name')
            current_user.phone = request.form.get('phone')
            if booking.status == "rejected" and new_date != old_date:
                booking.status = "pending"
                try:
                    msg = MailMessage(
                        subject="New Date Request — Lux Head Space Mobile Barber Concierge",
                        sender=current_app.config["MAIL_USERNAME"],
                        recipients=[current_app.config["BARBER_PHONE"]],
                    )
                    msg.body = f"{current_user.name} has submitted a new date request for {new_date} at {booking.venue}. Log in to review: http://127.0.0.1:5000/admin"
                    mail.send(msg)
                except Exception as e:
                    print(f"Notification failed: {e}")
                flash(
                    "Your new date has been submitted for review. We will confirm within 24 hours."
                )
            else:
                flash("Your booking has been updated!")
            db.session.commit()
            return redirect(url_for("portal"))
        return render_template("edit_booking.html", booking=booking)

    @app.route("/portal/messages", methods=["GET", "POST"])
    @login_required
    def portal_messages():
        booking = Booking.query.filter_by(user_id=current_user.id).first()
        if not booking:
            return redirect(url_for("portal"))
        if request.method == "POST":
            body = request.form.get("body")
            if body:
                from models import Message

                message = Message(
                    booking_id=booking.id, sender_id=current_user.id, body=body
                )
                db.session.add(message)
                db.session.commit()
        from models import Message

        messages = (
            Message.query.filter_by(booking_id=booking.id)
            .order_by(Message.timestamp)
            .all()
        )
        for message in messages:
            if message.sender_id != current_user.id:
                message.read = True
        db.session.commit()
        return render_template("messages.html", booking=booking, messages=messages)

    @app.route("/admin/booking/<int:id>/messages", methods=["GET", "POST"])
    @login_required
    @admin_required
    def admin_messages(id):
        booking = Booking.query.get_or_404(id)
        if request.method == "POST":
            body = request.form.get("body")
            if body:
                from models import Message

                message = Message(
                    booking_id=booking.id, sender_id=current_user.id, body=body
                )
                db.session.add(message)
                db.session.commit()
        from models import Message

        messages = (
            Message.query.filter_by(booking_id=booking.id)
            .order_by(Message.timestamp)
            .all()
        )
        for message in messages:
            if message.sender_id != current_user.id:
                message.read = True
        db.session.commit()
        return render_template(
            "admin/messages.html", booking=booking, messages=messages
        )

    @app.context_processor
    def inject_unread():
        if current_user.is_authenticated:
            from models import Message

            if current_user.role == "admin":
                unread = (
                    Message.query.filter_by(read=False)
                    .filter(Message.sender_id != current_user.id)
                    .count()
                )
            else:
                booking = Booking.query.filter_by(user_id=current_user.id).first()
                if booking:
                    unread = (
                        Message.query.filter_by(booking_id=booking.id, read=False)
                        .filter(Message.sender_id != current_user.id)
                        .count()
                    )
                else:
                    unread = 0
            return {"unread_count": unread}
        return {"unread_count": 0}

    @app.route("/admin/calendar")
    @login_required
    @admin_required
    def admin_calendar():
        bookings = Booking.query.order_by(Booking.wedding_date).all()
        from collections import Counter

        date_counts = Counter(b.wedding_date for b in bookings)
        conflict_dates = {date for date, count in date_counts.items() if count > 1}
        return render_template(
            "admin/calendar.html", bookings=bookings, conflict_dates=conflict_dates
        )

    @app.route("/forgot-password", methods=["GET", "POST"])
    def forgot_password():
        if request.method == "POST":
            email = request.form.get("email")
            user = User.query.filter_by(email=email).first()
            if user:
                from werkzeug.security import generate_password_hash

                temp_password = "".join(
                    random.choices(string.ascii_letters + string.digits, k=8)
                )
                user.password = generate_password_hash(temp_password)
                user.password_changed = False
                db.session.commit()
                try:
                    msg = MailMessage(
                        subject="Groom Suite — Password Reset",
                        sender=current_app.config["MAIL_USERNAME"],
                        recipients=[email],
                    )
                    msg.body = f"Your temporary password is: {temp_password}\n\nLog in and change it immediately."
                    mail.send(msg)
                    flash("A temporary password has been sent to your email.")
                except Exception as e:
                    print(f"Email failed: {e}")
                    flash(
                        f"Your temporary password is: <strong>{temp_password}</strong> — please save this now."
                    )
            else:
                flash("No account found with that email address.")
            return redirect(url_for("login"))
        return render_template("forgot_password.html")

    @app.route("/we-come-to-you")
    def we_come_to_you():
        return render_template("features/we_come_to_you.html")

    @app.route("/premium-experience")
    def premium_experience():
        return render_template("features/premium_experience.html")

    @app.route("/professional-results")
    def professional_results():
        return render_template("features/professional_results.html")

    @app.route("/groom-squad-ready")
    def groom_squad_ready():
        return render_template("features/groom_squad_ready.html")

    @app.route("/admin/booking/<int:id>/cancel")
    @login_required
    @admin_required
    def admin_cancel_booking(id):
        booking = Booking.query.get_or_404(id)
        booking.status = "cancelled"
        db.session.commit()
        flash("Booking has been cancelled.")
        return redirect(url_for("admin_dashboard"))

    @app.route("/portal/cancel", methods=["POST"])
    @login_required
    def cancel_booking():
        booking = Booking.query.filter_by(user_id=current_user.id).first()
        if booking and booking.status != "cancelled":
            booking.status = "cancelled"
            db.session.commit()
            try:
                msg = MailMessage(
                    subject="Booking Cancelled — Lux Head Space Mobile Barber Concierge",
                    sender=current_app.config["MAIL_USERNAME"],
                    recipients=[current_app.config["BARBER_PHONE"]],
                )
                msg.body = f"Booking cancelled by {current_user.name} for {booking.wedding_date} at {booking.venue}."
                mail.send(msg)
            except Exception as e:
                print(f"Cancel notification failed: {e}")
            flash("Your booking has been cancelled. Please contact us to reschedule.")
        return redirect(url_for("portal"))
    
    @app.route('/services')
    def services():
        return render_template('services.html')
    
    @app.route('/portal/pay-deposit')
    @login_required
    def pay_deposit():
        booking = Booking.query.filter_by(user_id=current_user.id).first()
        if not booking:
            return redirect(url_for('portal'))

        stripe.api_key = current_app.config['STRIPE_SECRET_KEY']

        member_count = len(booking.party_members)
        if booking.party_size == 1:
            total = 500
        elif booking.party_size <= 4:
            total = 1200
        else:
            additional = max(0, member_count - 4) * 300
            total = 1200 + additional

        deposit = int(total * 0.5)

        customer = stripe.Customer.create(
            email=current_user.email,
            name=current_user.name,
            metadata={'booking_id': booking.id, 'user_id': current_user.id}
        )

        booking.stripe_customer_id = customer.id
        db.session.commit()

        session = stripe.checkout.Session.create(
            customer=customer.id,
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Lux Head Space — 50% Deposit',
                        'description': f'Wedding grooming deposit for {booking.wedding_date} at {booking.venue}',
                    },
                    'unit_amount': deposit * 100,
                },
                'quantity': 1,
            }],
            mode='payment',
            payment_intent_data={
                'setup_future_usage': 'off_session',
                'capture_method': 'automatic',
            },
            success_url=url_for('payment_success', _external=True),
            cancel_url=url_for('portal', _external=True),
        )
        return redirect(session.url, code=303)

    @app.route('/payment-success')
    @login_required
    def payment_success():
        booking = Booking.query.filter_by(user_id=current_user.id).first()
        if booking:
            booking.status = 'deposit_paid'
            stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
            try:
                customer_id = booking.stripe_customer_id
                payment_methods = stripe.PaymentMethod.list(
                    customer=customer_id,
                    type='card'
                )
                if payment_methods.data:
                    booking.deposit_amount = payment_methods.data[0].id
            except Exception as e:
                print(f'Payment method save error: {e}')
            db.session.commit()
        flash('Your deposit has been received! Your booking is confirmed.')
        return redirect(url_for('portal'))
    
    @app.route('/admin/booking/<int:id>/charge-remaining')
    @login_required
    @admin_required
    def charge_remaining(id):
        booking = Booking.query.get_or_404(id)
        stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
        try:
            member_count = len(booking.party_members)
            if booking.party_size == 1:
                total = 500
            elif booking.party_size <= 4:
                total = 1200
            else:
                additional = max(0, member_count - 4) * 300
                total = 1200 + additional
            remaining = int(total * 0.5)
            if not booking.deposit_amount:
                flash('ALERT: No saved card found for this customer. Please ask the client to re-enter their payment details.')
                return redirect(url_for('booking_detail', id=booking.id))
            payment_intent = stripe.PaymentIntent.create(
                amount=remaining * 100,
                currency='usd',
                customer=booking.stripe_customer_id,
                payment_method=booking.deposit_amount,
                confirm=True,
                off_session=True,
            )
            booking.status = 'completed'
            db.session.commit()
            flash(f'Remaining balance of ${remaining} charged successfully!')
        except Exception as e:
            flash(f'ALERT: Payment failed — {str(e)}')
        return redirect(url_for('booking_detail', id=booking.id))
    

