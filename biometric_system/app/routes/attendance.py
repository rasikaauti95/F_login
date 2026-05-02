from flask import Blueprint, render_template, Response, jsonify, current_app
from flask_login import login_required, current_user
from app.models import User, Attendance
from app import db
from datetime import datetime, timedelta

attendance_bp = Blueprint('attendance', __name__)

# To prevent multiple stream instances from conflicting, we could use a global
# but for this simple app, we'll instantiate when the route is hit.
# Note: In a production app, accessing a single webcam from multiple threads/requests is problematic.
# This assumes a kiosk mode where only one stream is active.

@attendance_bp.route('/live')
@login_required
def live():
    if current_user.role != 'admin':
        return jsonify({"error": "Unauthorized"}), 403
    return render_template('attendance/live.html')

def mark_attendance(user_id):
    """Callback function used by the video stream to mark attendance."""
    user = User.query.get(int(user_id))
    if not user:
        return {"status": "User not found"}

    # Check debounce (e.g., 5 minutes)
    cooldown = current_app.config.get('ATTENDANCE_COOLDOWN_MINUTES', 5)
    cutoff_time = datetime.utcnow() - timedelta(minutes=cooldown)
    
    recent_attendance = Attendance.query.filter(
        Attendance.user_id == user.id,
        Attendance.timestamp >= cutoff_time
    ).first()

    if recent_attendance:
        return {"name": user.name, "status": "Already marked recently"}

    # Determine if late (e.g., after 9:00 AM)
    # This is a simplified logic. In a real system, it would depend on a schedule.
    current_hour = datetime.utcnow().hour
    status = 'present' if current_hour < 9 else 'late'

    new_attendance = Attendance(user_id=user.id, method='face', status=status)
    db.session.add(new_attendance)
    db.session.commit()

    return {"name": user.name, "status": f"Marked {status}"}

@attendance_bp.route('/stream')
@login_required
def stream():
    if current_user.role != 'admin':
        return jsonify({"error": "Unauthorized"}), 403
        
    from app.vision.camera import VideoCamera
    cam = VideoCamera(current_app.recognizer, current_app.detector)
    
    # We pass the app instance to the generator so it can use the app context
    app = current_app._get_current_object()
    
    return Response(cam.get_frame_for_stream(app, mark_attendance_callback=mark_attendance),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@attendance_bp.route('/api/recent')
@login_required
def recent_attendance():
    """API endpoint to fetch recent attendance records for the dashboard."""
    if current_user.role != 'admin':
        return jsonify({"error": "Unauthorized"}), 403
        
    records = Attendance.query.order_by(Attendance.timestamp.desc()).limit(10).all()
    
    results = []
    for r in records:
        results.append({
            "id": r.id,
            "name": r.user.name,
            "time": r.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "method": r.method,
            "status": r.status
        })
        
    return jsonify(results)
