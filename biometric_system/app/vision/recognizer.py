import face_recognition
import os
import pickle
import numpy as np

class FaceRecognizer:
    def __init__(self, encodings_dir, threshold=0.45):
        self.encodings_dir = encodings_dir
        self.threshold = threshold
        self.known_encodings = []
        self.known_user_ids = []
        self.load_encodings()

    def load_encodings(self):
        """Load all face encodings from the encodings directory into memory."""
        self.known_encodings = []
        self.known_user_ids = []
        
        if not os.path.exists(self.encodings_dir):
            os.makedirs(self.encodings_dir, exist_ok=True)
            return

        for filename in os.listdir(self.encodings_dir):
            if filename.endswith(".pkl"):
                user_id = filename.split('.')[0]
                filepath = os.path.join(self.encodings_dir, filename)
                try:
                    with open(filepath, 'rb') as f:
                        encoding = pickle.load(f)
                        self.known_encodings.append(encoding)
                        self.known_user_ids.append(user_id)
                except Exception as e:
                    print(f"Error loading encoding {filepath}: {e}")

    def reload(self):
        """Reload encodings, e.g., after a new registration."""
        self.load_encodings()

    def get_encoding(self, rgb_face_image):
        """
        Compute the 128-d encoding for a cropped face image.
        Image should be RGB.
        """
        # Ensure the numpy array is C-contiguous, which is required by dlib/pybind11
        rgb_face_image = np.ascontiguousarray(rgb_face_image)
        
        # Since we pass cropped face, the face is the whole image
        # We tell face_recognition the bounding box is the whole image to save time
        h, w = rgb_face_image.shape[:2]
        face_locations = [(0, w, h, 0)] # top, right, bottom, left
        
        encodings = face_recognition.face_encodings(rgb_face_image, known_face_locations=face_locations)
        if encodings:
            return encodings[0]
        return None

    def save_encoding(self, user_id, encoding):
        """Save a face encoding to disk."""
        filepath = os.path.join(self.encodings_dir, f"{user_id}.pkl")
        with open(filepath, 'wb') as f:
            pickle.dump(encoding, f)
        self.reload()

    def match(self, encoding):
        """
        Compare an encoding against stored encodings.
        Returns matched user_id or None.
        """
        if not self.known_encodings:
            return None

        # Calculate face distances
        face_distances = face_recognition.face_distance(self.known_encodings, encoding)
        
        if len(face_distances) == 0:
            return None

        best_match_index = np.argmin(face_distances)
        if face_distances[best_match_index] < self.threshold:
            return self.known_user_ids[best_match_index]
            
        return None
