import os
from app import create_app, db

app = create_app()

if __name__ == '__main__':
    # Ensure directories exist
    os.makedirs(app.config['ENCODING_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.config['DATA_DIR'], 'db'), exist_ok=True)
    
    with app.app_context():
        # Avoid creating tables here if we use Flask-Migrate or seeds.py
        # but for simplicity we can create all if they don't exist
        db.create_all()
        
    app.run(debug=True, host='0.0.0.0', port=5000)
