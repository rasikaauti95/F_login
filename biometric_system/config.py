import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'data', 'db', 'biometric.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Paths for data storage
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    ENCODING_FOLDER = os.path.join(DATA_DIR, 'encodings')
    
    # Biometric configuration
    RECOGNITION_THRESHOLD = 0.45
    ATTENDANCE_COOLDOWN_MINUTES = 5
