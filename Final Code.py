import cv2
import dlib
import math
import pygame
import smtplib
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt
import time  
import geocoder
from email.mime.image import MIMEImage

last_yawn_time = time.time()
pygame.mixer.init()
alarm_sound = pygame.mixer.Sound('r3.mp3')
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')

eye_closed_frames = 0
yawn_count = 0
alarm_duration = 50
alarm_active = False
t = 0
camera_active = False 
u=0
k=0
yawn_threshold = 50

def eye_aspect_ratio(eye):
    vertical_dist1 = math.dist(eye[1], eye[5])
    vertical_dist2 = math.dist(eye[2], eye[4])
    horizontal_dist = math.dist(eye[0], eye[3])
    ear = (vertical_dist1 + vertical_dist2) / (2.0 * horizontal_dist)
    return ear

def is_yawn(landmarks):
    global yawn_count, k
    upper_lip_indices = [52]
    lower_lip_indices = [58]

    upper_lip_y = sum(landmarks.part(i).y for i in upper_lip_indices) / len(upper_lip_indices)
    lower_lip_y = sum(landmarks.part(i).y for i in lower_lip_indices) / len(lower_lip_indices)
   
    lip_distance = lower_lip_y - upper_lip_y
    if yawn_count > 9 and k == 0:
        driver_name = window.name_input.text()
        send_email(driver_name)
        k = 1
    return lip_distance > yawn_threshold

def trigger_alarm(frame):
    global alarm_active, t, yawn_count
    print("Drowsiness detected - Alarm!")
    if not alarm_active:
        pygame.mixer.Sound.play(alarm_sound)
        alarm_active = True
        t += 1

        if t == 3 or yawn_count == 9:
            driver_name = window.name_input.text()
            # Capture frame before triggering alarm
            ret, frame = cap.read()
            if ret:
                send_email(driver_name, frame)


def stop_alarm():
    global alarm_active
    if alarm_active:
        alarm_sound.stop()
        alarm_active = False

def get_location():
    location = geocoder.ip('me')
    return location

def send_email(driver_name, frame):
    sender_email = "drowsinesshb@gmail.com"
    sender_password = "fbdg zazh umoy xdrf"
    recipient_email = "hb09082002@gmail.com"

    # Get location
    location = get_location()

    # Create a message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = f"Drowsiness Alert- {driver_name}"
    body = f"Hey Fleet owner,your driver {driver_name} is feeling sleepy. Please take action.\n"
    if location:
        body += f"Location: {location.city}, Latitude: {location.latlng[0]}, Longitude: {location.latlng[1]}"
    message.attach(MIMEText(body, "plain"))

    # Attach frame as image
    if frame is not None:
        img = cv2.imencode('.jpg', frame)[1].tobytes()
        img_part = MIMEImage(img)
        img_part.add_header('Content-Disposition', 'attachment', filename='snapshot.jpg')
        message.attach(img_part)

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, message.as_string())
        server.quit()
        print("Email sent to owner")
    except Exception as e:
        print("Email sending failed:", str(e))

class DrowsinessApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

    def initUI(self):
        self.setWindowTitle("Drowsiness Detection for Truck Driver")
        self.setGeometry(100, 100, 800, 800)

        self.name_label = QLabel("Enter Name:")
        self.name_input = QLineEdit()

        self.start_button = QPushButton("Start Detection")
        self.start_button.clicked.connect(self.start_d)

        self.stop_button = QPushButton("Stop Detection")
        self.stop_button.clicked.connect(self.stop_d)
        self.stop_button.setEnabled(False)

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close_app)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)

        l = QVBoxLayout()
        l.addWidget(self.name_label)
        l.addWidget(self.name_input)
        l.addWidget(self.start_button)
        l.addWidget(self.stop_button)
        l.addWidget(self.close_button)
        l.addWidget(self.image_label)
        self.setLayout(l)

    def start_d(self):
        global cap, camera_active
        driver_name = self.name_input.text()
        if not driver_name:
            QMessageBox.warning(self, "Warning", "Please enter the driver's name.")
            return
        if not camera_active:
            cap = cv2.VideoCapture(0)
            camera_active = True
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.timer.start(10)

    def stop_d(self):
        global cap, camera_active
        if camera_active:
            cap.release()
            camera_active = False
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.timer.stop()
        stop_alarm()

    def close_app(self):
        self.stop_d()
        self.close()

    def update_frame(self):
        global eye_closed_frames, yawn_count, last_yawn_time
        ret, frame = cap.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = detector(gray)

            for face in faces:
                landmarks = predictor(gray, face)
                x, y, w, h = face.left(), face.top(), face.width(), face.height()
                cv2.rectangle(frame_rgb, (x, y), (x + w, y + h), (0, 255, 0), 2)
                left_eye = [(landmarks.part(i).x, landmarks.part(i).y) for i in range(36, 42)]
                right_eye = [(landmarks.part(i).x, landmarks.part(i).y) for i in range(42, 48)]
                left_ear = eye_aspect_ratio(left_eye)
                right_ear = eye_aspect_ratio(right_eye)
                ear = (left_ear + right_ear) / 2.0
                
                if ear < 0.25:
                    eye_closed_frames += 1
                else:
                    eye_closed_frames = 0
                if eye_closed_frames >= alarm_duration:
                    trigger_alarm(frame)
                else:
                    stop_alarm()
                if is_yawn(landmarks):
                    current_time = time.time()
                    if current_time - last_yawn_time >= 2:
                        yawn_count += 1
                        last_yawn_time = current_time

                cv2.putText(frame_rgb, f"EAR: {ear:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.putText(frame_rgb, f"Eyes Closed: {t}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.putText(frame_rgb, f"Yawn Count {yawn_count}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_image = QImage(frame_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            self.image_label.setPixmap(pixmap)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DrowsinessApp()
    window.show()
    sys.exit(app.exec_())
