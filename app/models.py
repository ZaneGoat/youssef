from datetime import datetime
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='client') # 'admin' or 'client'
    reservations = db.relationship('Reservation', backref='author', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'

    def __repr__(self):
        return f'<User {self.username}>'

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Terrain(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    terrain_type = db.Column(db.String(32)) # e.g., 'football', 'basketball'
    description = db.Column(db.String(256))
    hourly_rate = db.Column(db.Float)
    image_url = db.Column(db.String(256))
    reservations = db.relationship('Reservation', backref='terrain', lazy='dynamic')

    def __repr__(self):
        return f'<Terrain {self.name}>'

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    terrain_id = db.Column(db.Integer, db.ForeignKey('terrain.id'))
    date = db.Column(db.Date, index=True)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    status = db.Column(db.String(20), default='pending') # 'pending', 'confirmed', 'cancelled'
    total_price = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return f'<Reservation {self.id} for {self.terrain_id}>'
