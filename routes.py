
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, User, Booking, PartyMember
from functools import wraps

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