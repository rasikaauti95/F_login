import cv2
import time
from datetime import datetime
from app.vision.detector import FaceDetector
from app.vision.recognizer import FaceRecognizer

class VideoCamera:
    def __init__(self, recognizer, detector):
        # 0 for default webcam
        self.video = cv2.VideoCapture(0)
        self.recognizer = recognizer
        self.detector = detector
        
    def __del__(self):
        self.video.release()

    def get_frame_for_stream(self, app, mark_attendance_callback=None):
        """
        Yields frames for MJPEG stream. Also processes attendance if callback provided.
        """
        while True:
            success, image = self.video.read()
            if not success:
                break
                
            # Resize for faster processing if needed
            # small_frame = cv2.resize(image, (0, 0), fx=0.5, fy=0.5)
            
            # Convert BGR to RGB for face_recognition
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Detect faces
            faces = self.detector.detect_faces(image)
            
            for (x1, y1, x2, y2, conf) in faces:
                # Draw bounding box
                cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # Crop and recognize
                # Only if we have a callback and confidence is somewhat high (e.g. > 0.5)
                if mark_attendance_callback and conf > 0.5:
                    rgb_face = rgb_image[y1:y2, x1:x2]
                    
                    # Compute encoding
                    encoding = self.recognizer.get_encoding(rgb_face)
                    
                    if encoding is not None:
                        # Match against known encodings
                        user_id = self.recognizer.match(encoding)
                        if user_id:
                            # We have a match, mark attendance
                            # Run inside app context since callback accesses DB
                            with app.app_context():
                                status_info = mark_attendance_callback(user_id)
                                
                            # Display name and status on frame
                            name = status_info.get('name', 'Unknown')
                            status = status_info.get('status', '')
                            
                            label = f"{name} - {status}"
                            cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        else:
                            cv2.putText(image, "Unknown", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # Encode frame to JPEG
            ret, jpeg = cv2.imencode('.jpg', image)
            frame = jpeg.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

    def capture_face_for_registration(self):
        """
        Captures a single frame, detects a face, and returns its encoding and the image.
        Used for registering new users.
        """
        success, image = self.video.read()
        if not success:
            return None, "Failed to capture video"
            
        faces = self.detector.detect_faces(image)
        if not faces:
            return None, "No face detected in frame"
            
        if len(faces) > 1:
            return None, "Multiple faces detected. Please ensure only one person is in frame."
            
        # Get the first (and only) face
        x1, y1, x2, y2, _ = faces[0]
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        rgb_face = rgb_image[y1:y2, x1:x2]
        
        encoding = self.recognizer.get_encoding(rgb_face)
        if encoding is None:
            return None, "Could not compute face encoding"
            
        return encoding, None

    def process_base64_image(self, base64_string):
        """
        Decodes a base64 image, detects a face, and returns its encoding.
        """
        import base64
        import numpy as np
        
        # Remove header if present (e.g., 'data:image/jpeg;base64,...')
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
            
        try:
            image_bytes = base64.b64decode(base64_string)
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                return None, "Failed to decode image"
                
            faces = self.detector.detect_faces(image)
            if not faces:
                return None, "No face detected in frame. Please ensure your face is clearly visible."
                
            if len(faces) > 1:
                return None, "Multiple faces detected. Please ensure only one person is in frame."
                
            x1, y1, x2, y2, _ = faces[0]
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            rgb_face = rgb_image[y1:y2, x1:x2]
            
            encoding = self.recognizer.get_encoding(rgb_face)
            if encoding is None:
                return None, "Could not compute face encoding"
                
            return encoding, None
        except Exception as e:
            return None, f"Error processing image: {str(e)}"
