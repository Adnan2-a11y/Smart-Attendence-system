import os
import cv2
import face_recognition
import logging
from openpyxl import Workbook
from datetime import datetime
from typing import List, Optional, Dict
import pickle
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("attendance.log"), logging.StreamHandler()],
)

# Constants
CONFIG = {
    "IMAGE_DIR": "student_images",
    "ENCODINGS_CACHE": "face_encodings.pkl",
    "CAMERA_INDEX": 0,
    "FRAME_SCALE_FACTOR": 0.25,  # Reduced for faster processing
    "MIN_FACE_CONFIDENCE": 0.5,  # Adjusted for better recognition balance
    "PROCESS_EVERY_N_FRAME": 2,  # Process every other frame
    "MAX_RETRY_ATTEMPTS": 3,
}

class AttendanceSystem:
    def __init__(self) -> None:
        self.known_encodings: List[List[float]] = []
        self.known_names: List[str] = []
        self.roll_mapping: Dict[str, int] = {}
        self.logged_this_session: set = set()
        self.id_counter: int = 1
        self.cap: Optional[cv2.VideoCapture] = None
        self.wb: Workbook = Workbook()
        self.frame_count = 0
        
        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.excel_file = f"attendance_{timestamp}.xlsx"
        self._init_excel()

    def _init_excel(self) -> None:
        """Initialize new Excel workbook for each session"""
        try:
            self.wb.active.append(
                ["ID", "Name", "Date", "Time", "Roll Number", "Presence Indicator"]
            )
            self.wb.save(self.excel_file)
            logging.info(f"Created new attendance file: {self.excel_file}")
        except Exception as e:
            logging.error(f"Excel initialization failed: {str(e)}")
            raise

    def _load_roll_mapping(self) -> None:
        """Load student name to roll number mapping"""
        self.roll_mapping = {
            "Jafir": 3,
            "Hasib": 10,
            "Hasan": 16,
            "NL RAFI": 17,
            "Zeeshan Ahmed":18,
            "Masrafi": 25,
            "Md.Sanzis Hasnat": 26,
            "Md.Rafshan Jani": 27,
        }

    def _load_face_encodings(self) -> None:
        """Load or generate face encodings with parallel processing"""
        if os.path.exists(CONFIG["ENCODINGS_CACHE"]):
            with open(CONFIG["ENCODINGS_CACHE"], "rb") as f:
                data = pickle.load(f)
                self.known_encodings = data["encodings"]
                self.known_names = data["names"]
            logging.info("Loaded face encodings from cache")
            return

        valid_extensions = {".jpg", ".jpeg", ".png"}
        encodings = []
        names = []

        try:
            for filename in os.listdir(CONFIG["IMAGE_DIR"]):
                if os.path.splitext(filename)[1].lower() not in valid_extensions:
                    continue

                name = os.path.splitext(filename)[0]
                if name not in self.roll_mapping:
                    continue

                image_path = os.path.join(CONFIG["IMAGE_DIR"], filename)
                image = face_recognition.load_image_file(image_path)
                face_encodings = face_recognition.face_encodings(image)
                
                if len(face_encodings) == 1:
                    encodings.append(face_encodings[0])
                    names.append(name)

            with open(CONFIG["ENCODINGS_CACHE"], "wb") as f:
                pickle.dump({"encodings": encodings, "names": names}, f)

            self.known_encodings = encodings
            self.known_names = names
            logging.info("Generated and cached new face encodings")

        except Exception as e:
            logging.error(f"Face encoding generation failed: {str(e)}")
            raise

    def _initialize_camera(self) -> None:
        """Initialize camera with optimized settings"""
        self.cap = cv2.VideoCapture(CONFIG["CAMERA_INDEX"])
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        if not self.cap.isOpened():
            logging.error("Failed to initialize camera")
            raise RuntimeError("Camera initialization failed")

    def process_frame(self, frame) -> None:
        """Optimized frame processing with frame skipping"""
        self.frame_count += 1
        if self.frame_count % CONFIG["PROCESS_EVERY_N_FRAME"] != 0:
            return

        try:
            small_frame = cv2.resize(frame, (0, 0), 
                                  fx=CONFIG["FRAME_SCALE_FACTOR"], 
                                  fy=CONFIG["FRAME_SCALE_FACTOR"])
            rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

            # Use faster face detection model (hog)
            face_locations = face_recognition.face_locations(rgb_frame, model="hog")
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            for encoding, location in zip(face_encodings, face_locations):
                matches = face_recognition.compare_faces(
                    self.known_encodings, encoding, 
                    tolerance=CONFIG["MIN_FACE_CONFIDENCE"]
                )
                
                if True in matches:
                    best_match = matches.index(True)
                    self._handle_recognized_face(best_match)

        except Exception as e:
            logging.error(f"Frame processing error: {str(e)}")

    def _handle_recognized_face(self, match_index: int) -> None:
        """Handle recognized face with batched write operations"""
        name = self.known_names[match_index]
        if name in self.logged_this_session:
            return

        current_time = datetime.now()
        try:
            self.wb.active.append([
                self.id_counter,
                name,
                current_time.strftime("%Y-%m-%d"),
                current_time.strftime("%H:%M:%S"),
                self.roll_mapping.get(name, "N/A"),
                1
            ])
            self.id_counter += 1
            self.logged_this_session.add(name)
            logging.info(f"Logged attendance for {name}")
        except Exception as e:
            logging.error(f"Failed to log {name}: {str(e)}")

    def run(self) -> None:
        """Optimized main loop with automatic saves"""
        last_save = time.time()
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    break

                self.process_frame(frame)
                cv2.imshow("Attendance System", frame)

                # Auto-save every 30 seconds
                if time.time() - last_save > 30:
                    self.wb.save(self.excel_file)
                    last_save = time.time()
                    logging.info("Auto-saved attendance records")

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

        except KeyboardInterrupt:
            logging.info("Shutting down gracefully...")
        finally:
            self._cleanup()

    def _cleanup(self) -> None:
        """Release resources and final save"""
        try:
            self.wb.save(self.excel_file)
            logging.info(f"Final attendance saved to {self.excel_file}")
            if self.cap and self.cap.isOpened():
                self.cap.release()
            cv2.destroyAllWindows()
        except Exception as e:
            logging.error(f"Cleanup error: {str(e)}")

    def initialize_system(self) -> None:
        """Initialize system components"""
        self._load_roll_mapping()
        self._load_face_encodings()
        self._initialize_camera()

if __name__ == "__main__":
    system = AttendanceSystem()
    try:
        system.initialize_system()
        system.run()
    except Exception as e:
        logging.critical(f"System failure: {str(e)}")
        exit(1)
