
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, User, Booking, PartyMember, Message
from functools import wraps
from flask_mail import Message as MailMessage
from flask import current_app
import random
import string

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def register_routes(app, mail):

    @app.route('/admin')
    @login_required
    @admin_required
    def admin_dashboard():
        bookings = Booking.query.order_by(Booking.wedding_date).all()
        total = len(bookings)
        pending = len([b for b in bookings if b.status == 'pending'])
        confirmed = len([b for b in bookings if b.status == 'confirmed'])
        from collections import Counter
        date_counts = Counter(b.wedding_date for b in bookings)
        conflict_dates = {date for date, count in date_counts.items() if count > 1}
        return render_template('admin/dashboard.html',
            bookings=bookings,
            total=total,
            pending=pending,
            confirmed=confirmed,
            conflict_dates=conflict_dates)

    @app.route('/admin/booking/<int:id>/confirm')
    @login_required
    @admin_required
    def confirm_booking(id):
        booking = Booking.query.get_or_404(id)
        booking.status = 'confirmed'
        db.session.commit()
        flash('Booking confirmed.')
        return redirect(url_for('admin_dashboard'))

    @app.route('/admin/booking/<int:id>/reject')
    @login_required
    @admin_required
    def reject_booking(id):
        booking = Booking.query.get_or_404(id)
        booking.status = 'rejected'
        db.session.commit()
        flash('Booking rejected.')
        return redirect(url_for('admin_dashboard'))

    @app.route('/portal')
    @login_required
    def portal():
        if current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        booking = Booking.query.filter_by(user_id=current_user.id).first()
        return render_template('portal.html', booking=booking)
    
    @app.route('/portal/add-member', methods=['POST'])
    @login_required
    def add_member():
        booking = Booking.query.filter_by(user_id=current_user.id).first()
        if booking:
            current_count = len(booking.party_members)
            if current_count >= booking.party_size:
                flash(f'ALERT: You have reached your maximum party size of {booking.party_size} members. To add more, please edit your booking to increase your party size.')
                return redirect(url_for('portal'))
            name = request.form.get('member_name')
            service = request.form.get('member_service')
            if name and service:
                role = request.form.get('member_role', 'Groomsman')
                member = PartyMember(
                    name=name,
                    role=role,
                    service=service,
                    booking_id=booking.id
                )
                db.session.add(member)
                db.session.commit()
                flash('Party member added!')
        return redirect(url_for('portal'))

    @app.route('/portal/remove-member/<int:id>')
    @login_required
    def remove_member(id):
        member = PartyMember.query.get_or_404(id)
        db.session.delete(member)
        db.session.commit()
        flash('Party member removed.')
        return redirect(url_for('portal'))

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/inquiry', methods=['GET', 'POST'])
    def inquiry():
        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            phone = request.form.get('phone')
            wedding_date = request.form.get('wedding_date')
            venue = request.form.get('venue')
            party_size_int = int(request.form.get('party_size'))
            if party_size_int == 1:
                package = 'Groom Only'
            elif party_size_int <= 4:
                package = 'Small Group Package'
            elif party_size_int <= 8:
                package = 'Full Squad Package'
            else:
                package = 'Large Party Package'
            addons = request.form.get('addons')
            notes = request.form.get('notes')

            existing_user = User.query.filter_by(email=email).first()
            if not existing_user:
                from werkzeug.security import generate_password_hash
                temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
                new_user = User(
                    name=name,
                    email=email,
                    phone=phone,
                    password=generate_password_hash(temp_password),
                    role='client'
                )
                db.session.add(new_user)
                db.session.flush()
                user_id = new_user.id
                try:
                    msg = MailMessage(
                        subject='New Booking Inquiry — Groom Suite',
                        sender=current_app.config['MAIL_USERNAME'],
                        recipients=[current_app.config['BARBER_PHONE']]
                    )
                    msg.body = f'New inquiry from {name} for {wedding_date} at {venue}. Log in to review: http://127.0.0.1:5000/admin'
                    mail.send(msg)
                except Exception as e:
                    print(f'SMS notification failed: {e}')
                flash(f'Welcome, {name}! Your inquiry has been submitted. Log in with your email and temporary password: <strong>{temp_password}</strong>')
            else:
                user_id = existing_user.id
                flash(f'Welcome back, {name}! Your new inquiry has been submitted.')

            booking = Booking(
                wedding_date=wedding_date,
                venue=venue,
                party_size=party_size_int,
                package=package,
                addons=addons,
                notes=notes,
                status='pending',
                user_id=user_id
            )
            db.session.add(booking)
            db.session.commit()
            return redirect(url_for('login'))

        return render_template('inquiry.html')

    @app.route('/about')
    def about():
        return render_template('about.html')

    @app.route('/change-password', methods=['GET', 'POST'])
    @login_required
    def change_password():
        if request.method == 'POST':
            from werkzeug.security import generate_password_hash
            new_password = request.form.get('new_password')
            confirm = request.form.get('confirm_password')
            if new_password != confirm:
                flash('Passwords do not match.')
                return redirect(url_for('change_password'))
            current_user.password = generate_password_hash(new_password)
            current_user.password_changed = True
            db.session.commit()
            flash('Password updated successfully!')
            return redirect(url_for('portal'))
        return render_template('change_password.html')
    
    @app.route('/admin/booking/<int:id>')
    @login_required
    @admin_required
    def booking_detail(id):
        booking = Booking.query.get_or_404(id)
        return render_template('admin/booking_detail.html', booking=booking)
    
    @app.route('/portal/edit', methods=['GET', 'POST'])
    @login_required
    def edit_booking():
        booking = Booking.query.filter_by(user_id=current_user.id).first()
        if not booking:
            return redirect(url_for('portal'))
        if request.method == 'POST':
            booking.wedding_date = request.form.get('wedding_date')
            booking.venue = request.form.get('venue')
            booking.party_size = int(request.form.get('party_size'))
            booking.package = request.form.get('package')
            booking.addons = request.form.get('addons')
            booking.notes = request.form.get('notes')
            current_user.name = request.form.get('name')
            current_user.phone = request.form.get('phone')
            db.session.commit()
            flash('Your booking has been updated!')
            return redirect(url_for('portal'))
        return render_template('edit_booking.html', booking=booking)
    
    @app.route('/portal/messages', methods=['GET', 'POST'])
    @login_required
    def portal_messages():
        booking = Booking.query.filter_by(user_id=current_user.id).first()
        if not booking:
            return redirect(url_for('portal'))
        if request.method == 'POST':
            body = request.form.get('body')
            if body:
                from models import Message
                message = Message(
                    booking_id=booking.id,
                    sender_id=current_user.id,
                    body=body
                )
                db.session.add(message)
                db.session.commit()
        from models import Message
        messages = Message.query.filter_by(booking_id=booking.id).order_by(Message.timestamp).all()
        for message in messages:
            if message.sender_id != current_user.id:
                message.read = True
        db.session.commit()
        return render_template('messages.html', booking=booking, messages=messages)

    @app.route('/admin/booking/<int:id>/messages', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def admin_messages(id):
        booking = Booking.query.get_or_404(id)
        if request.method == 'POST':
            body = request.form.get('body')
            if body:
                from models import Message
                message = Message(
                    booking_id=booking.id,
                    sender_id=current_user.id,
                    body=body
                )
                db.session.add(message)
                db.session.commit()
        from models import Message
        messages = Message.query.filter_by(booking_id=booking.id).order_by(Message.timestamp).all()
        for message in messages:
            if message.sender_id != current_user.id:
                message.read = True
        db.session.commit()
        return render_template('admin/messages.html', booking=booking, messages=messages)
    
    @app.context_processor
    def inject_unread():
        if current_user.is_authenticated:
            from models import Message
            if current_user.role == 'admin':
                unread = Message.query.filter_by(read=False).filter(
                    Message.sender_id != current_user.id).count()
            else:
                booking = Booking.query.filter_by(user_id=current_user.id).first()
                if booking:
                    unread = Message.query.filter_by(
                        booking_id=booking.id, read=False).filter(
                        Message.sender_id != current_user.id).count()
                else:
                    unread = 0
            return {'unread_count': unread}
        return {'unread_count': 0}
    
    @app.route('/admin/calendar')
    @login_required
    @admin_required
    def admin_calendar():
        bookings = Booking.query.order_by(Booking.wedding_date).all()
        from collections import Counter
        date_counts = Counter(b.wedding_date for b in bookings)
        conflict_dates = {date for date, count in date_counts.items() if count > 1}
        return render_template('admin/calendar.html', bookings=bookings, conflict_dates=conflict_dates)
    
    @app.route('/forgot-password', methods=['GET', 'POST'])
    def forgot_password():
        if request.method == 'POST':
            email = request.form.get('email')
            user = User.query.filter_by(email=email).first()
            if user:
                from werkzeug.security import generate_password_hash
                temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
                user.password = generate_password_hash(temp_password)
                user.password_changed = False
                db.session.commit()
                try:
                    msg = MailMessage(
                        subject='Groom Suite — Password Reset',
                        sender=current_app.config['MAIL_USERNAME'],
                        recipients=[email]
                    )
                    msg.body = f'Your temporary password is: {temp_password}\n\nLog in and change it immediately.'
                    mail.send(msg)
                    flash('A temporary password has been sent to your email.')
                except Exception as e:
                    print(f'Email failed: {e}')
                    flash(f'Your temporary password is: <strong>{temp_password}</strong> — please save this now.')
            else:
                flash('No account found with that email address.')
            return redirect(url_for('login'))
        return render_template('forgot_password.html')
    
    @app.route('/we-come-to-you')
    def we_come_to_you():
        return render_template('features/we_come_to_you.html')

    @app.route('/premium-experience')
    def premium_experience():
        return render_template('features/premium_experience.html')

    @app.route('/professional-results')
    def professional_results():
        return render_template('features/professional_results.html')

    @app.route('/groom-squad-ready')
    def groom_squad_ready():
        return render_template('features/groom_squad_ready.html')