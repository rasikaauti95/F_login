# Flogin: Smart Biometric Attendance and Login System

A smart biometric attendance and login system for a college environment built with Flask, OpenCV, YOLOv8, and `face_recognition`.

## Features
- **Face-based Login**: Authenticate users securely using facial recognition via webcam.
- **Automatic Attendance**: Live MJPEG video stream with real-time face detection (YOLOv8) and recognition to automatically mark attendance.
- **Admin Dashboard**: Manage users, register new users with face capture, and view live attendance logs.
- **Modern UI**: Built with Bootstrap 5, featuring a clean, responsive, glassmorphism-inspired design.

## Prerequisites
- Python 3.10+
- Webcam connected to the system.
- C++ Build Tools (required for compiling `dlib` during `face_recognition` installation). On Windows, install Visual Studio C++ Build Tools. On Linux, run `sudo apt-get install build-essential cmake`.

## Setup Instructions

1. **Clone the repository or navigate to the project directory:**
   ```bash
   cd biometric_system
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   *Note: If `face_recognition` fails to install, ensure CMake and a C++ compiler are installed.*

4. **YOLOv8 Model:**
   The application uses YOLOv8 for fast face detection. By default, it will look for `yolov8n-face.pt`. If you don't have it, standard `yolov8n.pt` will be downloaded automatically by the ultralytics library and used (though it might detect 'persons' instead of purely 'faces' without custom weights). For best results, place a trained YOLOv8 face model named `yolov8n-face.pt` in the project root.

5. **Initialize the Database:**
   Run the seed script to create the SQLite database, tables, and default users (including an admin account).
   ```bash
   python seeds.py
   ```
   *This creates an admin with email `admin@college.edu`.*

6. **Run the Application:**
   ```bash
   python run.py
   ```
   The application will start on `http://localhost:5000`.

## Quick Start Guide
1. Open `http://localhost:5000` in your browser.
2. Click **Manual Login** and use the email `admin@college.edu` to log in as the administrator.
3. Once in the **Admin Dashboard**, click **Register User** to add a new user and capture their face using your webcam.
4. Go to **Live Attendance** mode to start the real-time scanner. Anyone who steps in front of the camera and is registered will have their attendance marked automatically!
5. Log out and try the **Face Login** with the newly registered user.
