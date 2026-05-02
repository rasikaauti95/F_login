from ultralytics import YOLO
import cv2
import os

class FaceDetector:
    def __init__(self, model_path='yolov8n-face.pt'):
        # Initialize YOLOv8 model
        try:
            self.model = YOLO(model_path)
            self.model.fuse() # Fuse for faster inference
        except Exception as e:
            print(f"Warning: Could not load YOLO model from {model_path}. Error: {e}")
            self.model = None
            
        # Initialize OpenCV Haar Cascade as fallback
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)

    def detect_faces(self, frame):
        """
        Detect faces in a frame.
        Returns a list of tuples: (x1, y1, x2, y2, confidence)
        """
        faces = []
        
        # Try YOLO first
        if self.model is not None:
            results = self.model(frame, stream=True, verbose=False)
            for r in results:
                boxes = r.boxes
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0]
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    conf = float(box.conf[0])
                    
                    h, w = frame.shape[:2]
                    x1 = max(0, x1)
                    y1 = max(0, y1)
                    x2 = min(w, x2)
                    y2 = min(h, y2)
                    
                    if x2 > x1 and y2 > y1:
                        faces.append((x1, y1, x2, y2, conf))
            return faces
            
        # Fallback to OpenCV Haar Cascade
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # detectMultiScale returns (x, y, w, h)
        detected = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        
        for (x, y, w, h) in detected:
            # Haar doesn't give a confidence score in the same way, we'll assign 1.0
            faces.append((x, y, x+w, y+h, 1.0))
            
        return faces

    def crop_face(self, frame, box):
        """
        Crop the face region from the frame based on bounding box.
        """
        x1, y1, x2, y2, _ = box
        return frame[y1:y2, x1:x2]
