'''
Copyright (c) 2023 Apollo Timbers. All rights reserved.

This work is licensed under the terms of the Apache License 2.0.
For a copy, see https://github.com/apache/.github/blob/main/LICENSE.

Sophie robot project:

Security class module, focusing on providing an automated security system. It integrates a ZED stereo camera and various sensors to monitor an environment for 
potential security breaches. The system is capable of detecting motion and is planned to be equipped with AI audio analysis for detecting sounds like breaking glass, 
enhancing its security capabilities.

Note: This module is in active development. Future versions will include refined motion detection algorithms, real-time audio analysis for additional security features (Planned integration of audio analysis for breaking glass detection.), and improved error handling and logging for robustness and reliability

Current Features:

- Utilization of ZED stereo camera for high-resolution imaging.
- Motion detection using background subtraction and contour analysis with OpenCV.
- Text-to-speech functionality for audible alerts in case of security breaches.
- Time-based activation and deactivation of the security system.
- Logging system for tracking events, errors, and system status.
- Threaded implementation for concurrent processing of camera feed and monitoring tasks.
- Takes two pictures when a security breach is detected and saves to a folder with a date/time stamp
- Sends a email with image attachments of the event to user

Change log:

- First revision of code that is in a working state
- There is a place holder for a glass breaking monitor, this will need to be a trained AI model for accuracy and to reduce false-positives 
- Now takes a image when a security breach is detected and saves to a folder, of the frame the detection was made and one a half later
- Added email functionality
- Reduced log spam

Know issues:

- Has a issue where the ZED hangs and has trouble connecting to it, will be a future fix
- Email sending takes a good chunk of time to comeplete may need a seperate class for it, so it can detect quick before alerts
'''

import cv2
import numpy as np
import datetime
import time
import threading
import argparse
import pyzed.sl as sl
import logging
import sys
import pyttsx3
import os  
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Global variable for speaking state
is_speaking = False

# Configure logging
logging.basicConfig(filename='security_module.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Initialize a lock for the engine
engine_lock = threading.Lock()

# Set the speech rate and voice
engine.setProperty('rate', 120)
engine.setProperty('voice', 'english+f3')

# Define the parser object globally
parser = argparse.ArgumentParser(description="Run the security system")
parser.add_argument('--activation_time', type=str, default="09:00", help='Activation time (HH:MM)')
parser.add_argument('--deactivation_time', type=str, default="17:00", help='Deactivation time (HH:MM)')

class SecurityModule:
    def __init__(self, activation_time="09:00", deactivation_time="17:00", warmup_duration=10):
        logging.info("Initializing Security Module")
        
        self.is_security_mode_active = False  

        self.zed = None  # Initialize ZED camera attribute

        self.activation_time = datetime.datetime.strptime(activation_time, "%H:%M").time()
        self.deactivation_time = datetime.datetime.strptime(deactivation_time, "%H:%M").time() 
        self.warmup_duration = warmup_duration  # Warm-up duration in seconds
        self.start_time = datetime.datetime.now()  # Record the start time of the system


        try:
            self.initialize_camera()
            
            # Introduce a delay after camera initialization (e.g., 3 seconds)
            time.sleep(3)

            self.system_ready = False  # New flag to indicate system is ready

            self.recent_frame_paths = []  # List to store the paths of recent frames

            # Initialize other attributes
            self.background_subtractor = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=16, detectShadows=True)
            self.is_security_mode_active = False

            logging.info("Security Module initialized successfully")

        except Exception as e:
            logging.error(f"Exception during initialization: {e}")

        finally:
            # If initialization fails, close the camera
            if self.zed and not self.zed.is_opened():
                logging.info("Closing ZED camera due to initialization failure.")
                self.zed.close()
    def is_warmup_period(self):
        """Check if the system is still in the warm-up period."""
        current_time = datetime.datetime.now()
        elapsed_time = (current_time - self.start_time).total_seconds()
        return elapsed_time < self.warmup_duration

    def reactivate_camera_if_active(self):
        if self.is_security_mode_active:
            logging.info("Reactivate camera procedure initiated.")
            self.close_camera()
            self.initialize_camera()
            logging.info("Camera reactivation complete.")

    def initialize_camera(self):
        try:
            self.zed = sl.Camera()
            init = sl.InitParameters()
            init.camera_resolution = sl.RESOLUTION.HD1080
            init.depth_mode = sl.DEPTH_MODE.PERFORMANCE
            init.coordinate_units = sl.UNIT.MILLIMETER

            err = self.zed.open(init)
            if err != sl.ERROR_CODE.SUCCESS:
                logging.error(f"Failed to re-open ZED camera: {repr(err)}")
                return

            # Introduce a delay after camera re-initialization (e.g., 2 seconds)
            time.sleep(2)

            logging.info("ZED camera re-initialized successfully.")
        except Exception as e:
            logging.error(f"Exception during camera re-initialization: {e}")

    def start_monitoring_thread(self):
        self.monitor_thread = threading.Thread(target=self.monitor)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def close_camera(self):
        if self.zed:
            try:
                self.zed.close()
            except Exception as e:
                logging.error(f"Error closing camera: {e}")

    def check_time(self):
        current_time = datetime.datetime.now().time()
        if self.activation_time <= current_time < self.deactivation_time:
            return True
        else:
            return False
    def capture_and_save_frame(self, frame, suffix=""):
        """Capture and save a frame with a date/time stamp."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"security_capture_{timestamp}{suffix}.png"
        folder_path = "/home/nvidia/dev/Sophie/security_events"  # Update this to your desired folder
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        cv2.imwrite(os.path.join(folder_path, filename), frame)
        full_path = os.path.join(folder_path, filename)
        cv2.imwrite(full_path, frame)
    
        # Store the path of the saved frame
        self.recent_frame_paths.append(full_path)

    """
    Detect Motion Function: Real-time Motion Detection and Alerting

    This function is responsible for continuously monitoring the environment 
    using the ZED stereo camera. It captures frames from the camera and processes 
    them to detect motion. Motion detection is achieved through background subtraction 
    and contour analysis. If motion above a certain threshold is detected, the function 
    logs the event, triggers an audible alert, captures and saves images of the event, 
    and reinitializes the camera for continued monitoring.
    """


    def detect_motion(self):
        if not self.system_ready or self.is_warmup_period():
            return False  # Do not detect motion until system is ready and warm-up period is over

        # Create an RGBA sl.Mat object using self.zed
        image_zed = sl.Mat(self.zed.get_camera_information().camera_resolution.width,
                           self.zed.get_camera_information().camera_resolution.height,
                           sl.MAT_TYPE.U8_C4)

        # Capture image from ZED camera using self.zed
        if self.zed.grab() == sl.ERROR_CODE.SUCCESS:
            self.zed.retrieve_image(image_zed, sl.VIEW.LEFT)
            frame = image_zed.get_data()

            # Convert to grayscale
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Apply background subtraction
            fg_mask = self.background_subtractor.apply(gray_frame)
            _, thresh = cv2.threshold(fg_mask, 200, 255, cv2.THRESH_BINARY)

            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                if cv2.contourArea(contour) > 1500:  # Threshold for object size
                    # Motion detected
                    logging.warning("Security breach detected!")
                    self.speak("Security breach detected!")  # Text-to-speech alert

                    # Save the current frame
                    self.capture_and_save_frame(frame, suffix="_detection")

                    # Wait for 0.5 seconds and capture another frame
                    time.sleep(0.5)
                    if self.zed.grab() == sl.ERROR_CODE.SUCCESS:
                        self.zed.retrieve_image(image_zed, sl.VIEW.LEFT)
                        next_frame = image_zed.get_data()
                        self.capture_and_save_frame(next_frame, suffix="_post_detection")


                    # send email with captured frames
                    send_email("Motion Detected", "Motion has been detected by Sophie the home robot security system.", "example@gmail.com", attachments=self.recent_frame_paths)
                    logging.info("Email sent")

                    # Clear the list after sending the email
                    self.recent_frame_paths.clear()

                    return True  # Return True as motion is detected

        return False  # Return False if no motion is detected


    def detect_breaking_glass(self):
        # Placeholder for real-time audio analysis code
        # This would involve capturing audio and analyzing it for the sound signature of breaking glass
        # For simplicity, this function just returns False in this example
        return False

    def speak(self, text):
        def run_speak():
            global is_speaking
            if engine_lock.acquire(blocking=False):
                try:
                    logging.debug("Ready to speak.")
                    is_speaking = True
                    engine.say(text)
                    engine.runAndWait()
                finally:
                    is_speaking = False
                    engine_lock.release()

        threading.Thread(target=run_speak).start()

    """
    Monitor Method: Security System Activation and Motion Detection

    This method controls the operational state of the security system,
    activating it during specified hours and deactivating it otherwise.
    During active hours, it initially bypasses a set number of frames to
    allow the system to stabilize. After this warm-up period, it continuously
    monitors for security breaches using motion detection and other security
    features. If a breach is detected, it triggers appropriate alert mechanisms.

    """

    def monitor(self):
        frame_count = 0
        initial_frames_to_ignore = 20  # Number of frames to ignore at startup
        while True:
            try:
                if self.check_time():
                    if not self.is_security_mode_active:
                        logging.info("Activating security mode.")
                        self.is_security_mode_active = True
                    if frame_count < initial_frames_to_ignore:
                        frame_count += 1
                        continue

                    self.system_ready = True  # Set system as ready after initial frames

                    # Add your motion detection and other monitoring logic here
                    if self.detect_motion() or self.detect_breaking_glass():
                        #logging.warning("Security breach detected!")
                        #self.speak("Security breach detected!")  # Corrected method call

                else:
                    if self.is_security_mode_active:
                        logging.info("Deactivating security mode.")
                        self.is_security_mode_active = False

                time.sleep(0.5)

            except Exception as e:
                logging.error(f"An error occurred: {e}")

"""
Send Email Function: Alert Notification via Email

This function is designed to send email notifications in the event of a security breach. 
It constructs an email with a specified subject and body, attaches images captured during 
the motion detection event, and sends it to a predefined recipient. The function uses 
SMTP for email transmission, ensuring that alerts are promptly delivered. 
"""

def send_email(subject, body, to_email, attachments=None):
    try:
        # Email credentials and server information
        from_email = "example@gmail.com"  # Replace with your email
        password = "phbn vgld elck vucp"  # Replace with your email password
        smtp_server = "smtp.gmail.com"
        smtp_port = 587  # For TLS

        # Create message
        message = MIMEMultipart()
        message["From"] = from_email
        message["To"] = to_email
        message["Subject"] = subject

        # Attach the body of the email to the message
        message.attach(MIMEText(body, "plain"))

        # Attach files
        if attachments:
            for file in attachments:
                part = MIMEBase('application', "octet-stream")
                with open(file, 'rb') as file_attachment:
                    part.set_payload(file_attachment.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment; filename="{}"'.format(os.path.basename(file)))
                message.attach(part)

        # Connect to the server and send the email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Secure the connection
        server.login(from_email, password)
        server.send_message(message)
        server.quit()

        print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")

def main():
   args = parser.parse_args()

   warmup_duration = 5  # 5 seconds warm-up time
   security_system = SecurityModule(activation_time=args.activation_time, deactivation_time=args.deactivation_time, warmup_duration=warmup_duration)
   security_system.start_monitoring_thread()

   # Keep the main thread alive or wait for a stop signal
   try:
       while True:
           time.sleep(1)
   except KeyboardInterrupt:
       # Handle graceful exit
       logging.info("Shutting down security system.")
       security_system.close_camera()


if __name__ == "__main__":
    main()

# Example usage
#security_system = python security_module.py --activation_time "09:15" --deactivation_time "17:00"
