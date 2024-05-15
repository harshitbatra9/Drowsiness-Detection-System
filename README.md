# Drowsiness-Detection-System
Drowsiness Detection for Truck Drivers
This project is a Python-based application that detects drowsiness in truck drivers using computer vision techniques. It analyzes the driver's facial features, such as eye closure and yawning, to determine their level of alertness. When drowsiness is detected, the system triggers an alarm and can send an alert email to the fleet owner.

Features
Real-time monitoring of the driver's face using a webcam.
Detection of eye closure and yawns to determine drowsiness.
Triggering an alarm when drowsiness is detected.
Sending an email alert to the fleet owner with a snapshot of the driver's face.
Prerequisites
Before running the application, make sure you have the following installed:

Python 3.x
OpenCV (pip install opencv-python)
Dlib (pip install dlib)
Pygame (pip install pygame)
PyQt5 (pip install pyqt5)
Geocoder (pip install geocoder)
Usage
Clone the repository to your local machine:

bash
Copy code
git clone https://github.com/your_username/drowsiness-detection.git
Navigate to the project directory:

bash
Copy code
cd drowsiness-detection
Run the application:

Copy code
python drowsiness_detection.py
Enter the driver's name in the provided input field and click "Start Detection" to begin monitoring.

To stop the detection process, click "Stop Detection" or simply close the application window.

Notes
Make sure your webcam is properly connected and accessible.
Adjust the alarm_duration and yawn_threshold variables in the drowsiness_detection.py file to fine-tune the sensitivity of the detection algorithm.
You may need to install additional dependencies or libraries based on your operating system and environment setup.

Authors
Harshit Batra
Trisha Srivastava
