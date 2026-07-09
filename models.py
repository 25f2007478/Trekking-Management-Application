from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__='users'

    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    gender = db.Column(db.String, nullable=False)
    dob = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    role = db.Column(db.String, nullable=False)
    m_no = db.Column(db.String, nullable=True)
    is_approved = db.Column(db.Boolean, default=True)

    # --- RELATIONSHIPS ---
    # 1. User <-> Staff Profile (One-to-One)
    staff_profile = db.relationship('StaffProfile', backref='user', uselist=False)
    # 2. User <-> Booking (One-to-Many)
    bookings = db.relationship('Booking', backref='user')

class StaffProfile(db.Model):
    __tablename__ = 'staff_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False, unique=True)
    speciality = db.Column(db.String(50), nullable=True) 
    status = db.Column(db.String(20), default='Available') 

    # --- RELATIONSHIPS --- 
    # Trek Staff <-> Trek (One-to-Many)
    assigned_treks = db.relationship('Trek', backref='staff_profile')

    
class Trek(db.Model):
    __tablename__ = 'treks'
    
    id = db.Column(db.Integer, primary_key=True)
    trek_name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(50), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False) 
    start_date = db.Column(db.String(20), nullable=False)
    end_date = db.Column(db.String(20), nullable=False)
    available_slots = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='Open') 
    img = db.Column(db.String(100), unique=True, nullable=False)
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey('staff_profiles.id'), nullable=True)
    
    # --- RELATIONSHIPS ---
    # Trek <-> Booking (One-to-Many)
    bookings = db.relationship('Booking', backref='trek')

class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey('treks.id'), nullable=False)
    
    booking_status = db.Column(db.String(20), default='Confirmed') 
    payment_status = db.Column(db.String(20), default='Pending') 
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)

    