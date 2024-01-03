'''
Copyright (c) 2023 Apollo Timbers. All rights reserved.

This work is licensed under the terms of the MIT license.
For a copy, see <https://opensource.org/licenses/MIT>.

Sophie robot project:

Chat GPT 4 image inference module *experimental

A test of the gpt-4-vision-preview. It takes a image from the ZED camera passes it to GPT and it analizes and sends back text, the robot then speaks what it "sees". It is interesting, would need to find
a way to have the robot do actions based on it. It also takes takes around 20 seconds with a TX2, using a lower resolution does not seem to work, even with treading on to speak sooner. Could be used to 
evaluate a room when first entering to know what home care task needs to be done. It merits more experimentation 
'''

import cv2
import pyzed.sl as sl
import pyttsx3
import base64
import requests
from datetime import datetime
import os
import threading  # Add this at the top of your script

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Set the speech rate and voice
engine.setProperty('rate', 120)
engine.setProperty('voice', 'english+f3')

def capture_image():
    # Initialize the ZED camera
    zed = sl.Camera()

    # Set configuration parameters
    init_params = sl.InitParameters()
    init_params.camera_resolution = sl.RESOLUTION.HD2K # or other desired resolution, lower - sl.RESOLUTION.HD1080  
    init_params.depth_mode = sl.DEPTH_MODE.NONE  # or other desired mode

    # Open the camera
    err = zed.open(init_params)
    if err != sl.ERROR_CODE.SUCCESS:
        exit(1)

    # Capture image
    image = sl.Mat()
    if zed.grab() == sl.ERROR_CODE.SUCCESS:
        zed.retrieve_image(image, sl.VIEW.LEFT)  # Retrieve the left image
        image_ocv = image.get_data()  # Convert to OpenCV format

	# Flip the image horizontally
        # image_ocv = cv2.flip(image_ocv, 1)

        # Specify the folder to save images
        save_folder = "/home/nvidia/dev/Sophie/Photos"
        os.makedirs(save_folder, exist_ok=True)  # Create the folder if it does not exist

        # Generate a unique filename with date and time
        filename = datetime.now().strftime("%Y%m%d_%H%M%S") + ".png"
        full_path = os.path.join(save_folder, filename)

        # Save the image
        cv2.imwrite(full_path, image_ocv)

        # Close the camera
        zed.close()

        return full_path

    # Close the camera in case of grab failure
    zed.close()
    return None

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def send_image_to_gpt4_vision(base64_image, api_key):
    headers = {
      "Content-Type": "application/json",
      "Authorization": f"Bearer {api_key}"
    }

    payload = {
      "model": "gpt-4-vision-preview",
      "messages": [
        {
          "role": "user",
          "content": [
            {"type": "text", "text": "Divide up the image into 9 quadrants, dont state what you are doing just say top left, top center so forth, then just list what is seen be concise"}, #"What’s in this image?, also do not reply with asterisk's"
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
          ]
        }
      ],
      "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    return response.json()['choices'][0]['message']['content']

def text_to_speech(text):
    def run_speak():
        engine.say(text)
        engine.runAndWait()

    threading.Thread(target=run_speak).start()

def main():
    api_key = 'your_api_key'
    image_path = capture_image()

    if image_path:
        base64_image = encode_image(image_path)
        description = send_image_to_gpt4_vision(base64_image, api_key)
        text_to_speech(description)
    else:
        print("Failed to capture image.")

if __name__ == "__main__":
    main()
