
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='client')
    phone = db.Column(db.String(20))
    password_changed = db.Column(db.Boolean, default=False)
    bookings = db.relationship('Booking', backref='client', lazy=True)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    wedding_date = db.Column(db.String(50), nullable=False)
    venue = db.Column(db.String(200), nullable=False)
    start_time = db.Column(db.String(20))
    party_size = db.Column(db.Integer, default=1)
    package = db.Column(db.String(100))
    addons = db.Column(db.String(200))
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    party_members = db.relationship('PartyMember', backref='booking', lazy=True)
    messages = db.relationship('Message', backref='booking_messages', lazy=True, foreign_keys='Message.booking_id')

class PartyMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    service = db.Column(db.String(100), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    body = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    read = db.Column(db.Boolean, default=False)
    
    sender = db.relationship('User', foreign_keys=[sender_id])
    booking = db.relationship('Booking', foreign_keys=[booking_id])