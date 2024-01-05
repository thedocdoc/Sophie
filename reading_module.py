'''
Copyright (c) 2022 Apollo Timbers. All rights reserved.

This work is licensed under the terms of the MIT license.  
For a copy, see <https://opensource.org/licenses/MIT>.

Sophie robot project:

reading physical books/notes module

This reads in a image fro the ZED to OpenCV then does some preprocessing steps to then feeds into pytesseract. Pytesseract then translates the words on the image and prints as a string python tts. This allows the robot to read text put in front of it, works well with black text on white background.

- Added getting a image from the ZED 
- Changed to python text to speech 
'''

import subprocess
import cv2
import pytesseract
import pyttsx3

def capture_image_with_zed():
    try:
        # Run the zed_snap.py script and capture its output
        result = subprocess.run(['python', 'zed_snap.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        if result.returncode != 0:
            print("Error capturing image with ZED camera: " + result.stderr)
            return None
        return result.stdout.strip()
    except Exception as e:
        print("An error occurred: " + str(e))
        return None

def read_image_and_convert_to_speech(image_path):
    # Initialize pyttsx3 engine
    engine = pyttsx3.init()
    engine.setProperty('rate', 120) # slow down speech
    engine.setProperty('voice', 'english+f3') # set to a "female" voice

    # Load and process the image
    image = cv2.imread(image_path)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur_image = cv2.medianBlur(gray_image, 3)
    img_rgb = cv2.cvtColor(blur_image, cv2.COLOR_BGR2RGB)

    # Extract text and convert to speech
    text = pytesseract.image_to_string(img_rgb)
    engine.say(text)
    engine.runAndWait()

def main():
    image_path = capture_image_with_zed()
    if image_path:
        read_image_and_convert_to_speech(image_path)

if __name__ == "__main__":
    main()
