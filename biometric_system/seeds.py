import os
from app import create_app, db
from app.models import User, Attendance
from datetime import datetime, timedelta
import random

app = create_app()

def seed_database():
    with app.app_context():
        # Create database and tables
        db.create_all()
        
        # Check if admin already exists
        admin_email = 'admin@college.edu'
        if User.query.filter_by(email=admin_email).first():
            print("Database already seeded with users. Checking for attendance records...")
        else:
            print("Seeding users...")
            # Create admin
            admin = User(
                name='System Administrator',
                email=admin_email,
                role='admin'
            )
            db.session.add(admin)
            
            # Create sample users
            sample_users = [
                User(name='Alice Smith', email='alice@college.edu', role='student', roll_number='2024CS001', department='Computer Science', semester='4th'),
                User(name='Bob Jones', email='bob@college.edu', role='student', roll_number='2024IT005', department='Information Technology', semester='2nd'),
                User(name='Charlie Brown', email='charlie@college.edu', role='staff', department='Registrar Office')
            ]
            
            for u in sample_users:
                db.session.add(u)
            
            db.session.commit()
            print("Users seeded.")

        # Seed attendance for students
        students = User.query.filter_by(role='student').all()
        if not students:
            print("No students found to seed attendance.")
            return

        print("Seeding attendance records...")
        now = datetime.utcnow()
        
        for student in students:
            # Add records for the last 15 days
            for i in range(15):
                date = now - timedelta(days=i)
                
                # Skip weekends
                if date.weekday() >= 5:
                    continue
                
                # Randomly decide status
                rand = random.random()
                if rand < 0.1: # 10% chance absent
                    status = 'absent'
                    # For absent, we still create a record so it shows up in the log as requested
                    # In a real system, you might have a different way to track absences
                    attendance = Attendance(
                        user_id=student.id,
                        timestamp=date.replace(hour=9, minute=0),
                        status=status,
                        method='manual'
                    )
                    db.session.add(attendance)
                elif rand < 0.3: # 20% chance late
                    status = 'late'
                    attendance = Attendance(
                        user_id=student.id,
                        timestamp=date.replace(hour=9, minute=random.randint(5, 45)),
                        status=status,
                        method='face'
                    )
                    db.session.add(attendance)
                else: # 70% chance present
                    status = 'present'
                    attendance = Attendance(
                        user_id=student.id,
                        timestamp=date.replace(hour=8, minute=random.randint(30, 59)),
                        status=status,
                        method='face'
                    )
                    db.session.add(attendance)
        
        db.session.commit()
        print("Attendance records seeded successfully.")

if __name__ == '__main__':
    seed_database()
