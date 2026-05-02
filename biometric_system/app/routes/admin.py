from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.models import User, Attendance
from app import db
import os

admin_bp = Blueprint('admin', __name__)

@admin_bp.before_request
@login_required
def require_admin():
    if current_user.role != 'admin':
        flash('Admin access required.', 'danger')
        return redirect(url_for('auth.profile'))

@admin_bp.route('/dashboard')
def dashboard():
    users_count = User.query.count()
    attendance_count = Attendance.query.count()
    users = User.query.all()
    return render_template('admin/dashboard.html', users=users, users_count=users_count, attendance_count=attendance_count)

@admin_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        role = request.form.get('role', 'student')
        capture_face = request.form.get('capture_face') == 'on'
        
        if not name or not email:
            flash('Name and email are required.', 'danger')
            return redirect(url_for('admin.register'))
            
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered.', 'danger')
            return redirect(url_for('admin.register'))
            
        new_user = User(name=name, email=email, role=role)
        db.session.add(new_user)
        db.session.flush() # Get user ID
        
        if capture_face:
            base64_image = request.form.get('base64_image')
            if not base64_image:
                flash('Face capture is enabled but no image was provided.', 'danger')
                return redirect(url_for('admin.register'))
                
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
                    flash('User registered and face captured successfully.', 'success')
                else:
                    flash('Face captured but encoding failed.', 'warning')
            except Exception as e:
                flash(f"Error accessing camera: {e}", 'danger')
        else:
            flash('User registered without face encoding.', 'success')
            
        db.session.commit()
        return redirect(url_for('admin.dashboard'))
        
    return render_template('admin/register.html')

@admin_bp.route('/user/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot delete yourself.', 'danger')
        return redirect(url_for('admin.dashboard'))
        
    # Delete encoding file if exists
    if user.face_encoding_path:
        filepath = os.path.join(current_app.config['ENCODING_FOLDER'], user.face_encoding_path)
        if os.path.exists(filepath):
            os.remove(filepath)
            
    # Also reload recognizer to remove from memory
    current_app.recognizer.reload()
            
    # Delete attendance records
    Attendance.query.filter_by(user_id=user.id).delete()
    
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully.', 'success')
    return redirect(url_for('admin.dashboard'))
