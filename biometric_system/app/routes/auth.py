from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, session
from flask_login import login_user, logout_user, current_user
from app.models import User
import cv2
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/', methods=['GET', 'POST'])
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        else:
            # Normal users just see a simple dashboard or get redirected
            return redirect(url_for('auth.profile'))

    if request.method == 'POST':
        # Manual login fallback (email/password) - if implemented. 
        # For this system, we'll assume email + some basic auth or just face login.
        # But we need a fallback for admin first time.
        email = request.form.get('email')
        if email:
            user = User.query.filter_by(email=email).first()
            if user:
                login_user(user)
                flash('Logged in successfully.', 'success')
                if user.role == 'admin':
                    return redirect(url_for('admin.dashboard'))
                return redirect(url_for('auth.profile'))
            else:
                flash('Invalid email.', 'danger')

    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('auth.profile'))

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        role = request.form.get('role', 'student')
        capture_face = request.form.get('capture_face') == 'on'

        if not name or not email:
            flash('Name and email are required.', 'danger')
            return redirect(url_for('auth.register'))

        from app import db
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered.', 'danger')
            return redirect(url_for('auth.register'))

        from sqlalchemy.exc import IntegrityError
        
        new_user = User(name=name, email=email, role=role)
        db.session.add(new_user)
        
        try:
            db.session.flush() # Get user ID
        except IntegrityError:
            db.session.rollback()
            flash('Email already registered (or submission was duplicated).', 'danger')
            return redirect(url_for('auth.register'))

        if capture_face:
            base64_image = request.form.get('base64_image')
            if not base64_image:
                db.session.rollback()
                flash('Face capture is enabled but no image was provided.', 'danger')
                return redirect(url_for('auth.register'))
                
            try:
                from app.vision.camera import VideoCamera
                cam = VideoCamera(current_app.recognizer, current_app.detector)
                encoding, error = cam.process_base64_image(base64_image)

                if error:
                    flash(f"Failed to process face: {error}", 'warning')
                elif encoding is not None:
                    # Save encoding
                    current_app.recognizer.save_encoding(str(new_user.id), encoding)
                    new_user.face_encoding_path = f"{new_user.id}.pkl"
                    flash('Registration successful! Face enrolled.', 'success')
                else:
                    flash('Registration successful, but face encoding failed.', 'warning')
            except Exception as e:
                db.session.rollback()
                flash(f"Error accessing camera: {e}", 'danger')
                return redirect(url_for('auth.register'))
        else:
            flash('Registration successful without face enrollment.', 'success')

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')
            return redirect(url_for('auth.register'))
            
        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth_bp.route('/login/face', methods=['POST'])
def face_login():
    """Endpoint for face login. Reads a frame from the webcam."""
    if 'face_login_attempts' not in session:
        session['face_login_attempts'] = 0

    if session['face_login_attempts'] >= 3:
        flash('Account locked due to 3 failed face login attempts.', 'danger')
        return redirect(url_for('auth.login'))

    try:
        base64_image = request.form.get('base64_image')
        if not base64_image:
            flash('No image captured.', 'danger')
            return redirect(url_for('auth.login'))
            
        from app.vision.camera import VideoCamera
        cam = VideoCamera(current_app.recognizer, current_app.detector)
        encoding, error = cam.process_base64_image(base64_image)
        
        if error:
            session['face_login_attempts'] += 1
            flash(f"Login failed: {error}", 'danger')
            return redirect(url_for('auth.login'))

        if encoding is not None:
            user_id = current_app.recognizer.match(encoding)
            if user_id:
                user = User.query.get(int(user_id))
                if user:
                    login_user(user)
                    session.pop('face_login_attempts', None)
                    flash(f'Welcome back, {user.name}!', 'success')
                    if user.role == 'admin':
                        return redirect(url_for('admin.dashboard'))
                    return redirect(url_for('auth.profile'))

        session['face_login_attempts'] += 1
        flash('Face not recognized.', 'danger')
    except Exception as e:
        flash(f"Error accessing camera: {e}", 'danger')

    return redirect(url_for('auth.login'))

@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile')
def profile():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    return render_template('profile.html', user=current_user)
