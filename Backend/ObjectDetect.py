import cv2
import torch
import json
import os
import time
import pyttsx3
from ultralytics import YOLO

class ObjectDetection:
    def __init__(self):
        self.model = YOLO("yolov8n.pt")  # Load YOLOv8 model
        self.cap = cv2.VideoCapture(0)   # Access camera
        self.speech_engine = pyttsx3.init()  # Initialize text-to-speech engine
        self.detected_objects = {}  # Store detected objects
        self.data_file = "Detections.json"  # Path to store detections

        # Ensure the data file exists
        if not os.path.exists(self.data_file):
            with open(self.data_file, "w") as f:
                json.dump({}, f)

    def speak(self, text):
        """Speak out detected objects."""
        self.speech_engine.say(text)
        self.speech_engine.runAndWait()

    def log_detection(self, obj_name):
        """Log detections in a JSON file."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        if obj_name in self.detected_objects:
            self.detected_objects[obj_name]["count"] += 1
            self.detected_objects[obj_name]["last_seen"] = timestamp
        else:
            self.detected_objects[obj_name] = {"count": 1, "last_seen": timestamp}

        with open(self.data_file, "w") as f:
            json.dump(self.detected_objects, f, indent=4)

    def detect_objects(self):
        """Perform real-time object detection and announce detected objects."""
        announced_objects = set()  # Keep track of announced objects

        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            results = self.model(frame)  # Perform object detection
            for result in results:
                for box in result.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    class_id = int(box.cls[0])
                    label = self.model.names[class_id]  # Get object name

                    # Draw bounding box and label
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                    # Speak and log object if new
                    if label not in announced_objects:
                        self.speak(f"I see a {label}")
                        announced_objects.add(label)
                        self.log_detection(label)

            cv2.imshow("Object Detection", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    detector = ObjectDetection()
    detector.detect_objects()

