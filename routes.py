
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, User, Booking, PartyMember
from functools import wraps
import random
import string

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def register_routes(app):

    @app.route('/admin')
    @login_required
    @admin_required
    def admin_dashboard():
        bookings = Booking.query.order_by(Booking.wedding_date).all()
        total = len(bookings)
        pending = len([b for b in bookings if b.status == 'pending'])
        confirmed = len([b for b in bookings if b.status == 'confirmed'])
        return render_template('admin/dashboard.html',
            bookings=bookings,
            total=total,
            pending=pending,
            confirmed=confirmed)

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
                flash(f'You have reached your maximum party size of {booking.party_size} members.')
                return redirect(url_for('portal'))
            name = request.form.get('member_name')
            service = request.form.get('member_service')
            if name and service:
                member = PartyMember(
                    name=name,
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
            party_size = request.form.get('party_size')
            package = request.form.get('package')
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
                flash(f'Welcome, {name}! Your inquiry has been submitted. Log in with your email and temporary password: <strong>{temp_password}</strong>')
            else:
                user_id = existing_user.id
                flash(f'Welcome back, {name}! Your new inquiry has been submitted.')

            booking = Booking(
                wedding_date=wedding_date,
                venue=venue,
                party_size=int(party_size),
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