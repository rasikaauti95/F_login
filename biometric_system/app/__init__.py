from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)

    # Initialize vision components
    from app.vision.detector import FaceDetector
    from app.vision.recognizer import FaceRecognizer
    
    app.detector = FaceDetector()
    app.recognizer = FaceRecognizer(app.config['ENCODING_FOLDER'], app.config['RECOGNITION_THRESHOLD'])

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.attendance import attendance_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(attendance_bp, url_prefix='/attendance')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    return app
