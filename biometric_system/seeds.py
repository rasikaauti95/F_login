import os
from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()

def seed_database():
    with app.app_context():
        # Create database and tables
        db.create_all()
        
        # Check if admin already exists
        if User.query.filter_by(email='admin@college.edu').first():
            print("Database already seeded.")
            return

        print("Seeding database...")
        
        # Create admin
        admin = User(
            name='System Administrator',
            email='admin@college.edu',
            role='admin'
        )
        db.session.add(admin)
        
        # Create sample users
        sample_users = [
            User(name='Alice Smith', email='alice@college.edu', role='student'),
            User(name='Bob Jones', email='bob@college.edu', role='student'),
            User(name='Charlie Brown', email='charlie@college.edu', role='staff')
        ]
        
        for u in sample_users:
            db.session.add(u)
            
        db.session.commit()
        print("Database seeded successfully with 1 admin and 3 sample users.")
        print("Admin login: email='admin@college.edu' (Manual login route or Face login if enrolled)")

if __name__ == '__main__':
    seed_database()
