from datetime import datetime
from flask_login import UserMixin
from app import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    roll_number = db.Column(db.String(20), unique=True, nullable=True)
    department = db.Column(db.String(100), nullable=True)
    semester = db.Column(db.String(20), nullable=True)
    role = db.Column(db.String(20), nullable=False, default='student') # 'student', 'staff', 'admin'
    face_encoding_path = db.Column(db.String(255), nullable=True) # Path to the .pkl file
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    attendances = db.relationship('Attendance', backref='user', lazy=True)

    def __repr__(self):
        return f"User('{self.name}', '{self.email}', '{self.role}')"

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    method = db.Column(db.String(20), nullable=False, default='face') # 'face', 'manual'
    status = db.Column(db.String(20), nullable=False, default='present') # 'present', 'late'

    def __repr__(self):
        return f"Attendance('{self.user_id}', '{self.timestamp}', '{self.status}')"
