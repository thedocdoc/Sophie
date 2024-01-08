'''
Copyright (c) 2022 Apollo Timbers. All rights reserved.

This work is licensed under the terms of the Apache License 2.0.
For a copy, see https://github.com/apache/.github/blob/main/LICENSE.

Sophie robot project:

reading physical books/notes module

This reads in a image fro the ZED to OpenCV then does some preprocessing steps to then feeds into pytesseract. 
Pytesseract then translates the words on the image and prints as a string python tts. 
This allows the robot to read text put in front of it, works well with black text on white background.

- Added getting a image from the ZED
- Changed to python text to speech
- heavily modified the pipeline to scale the image and box the text to help the OCR be faster and more accurate
- Need to have scale adjust more automatically, also I think adding auto adjustment of teh contrast/treshold may help in differnt lighting situations. 
'''

import subprocess
import cv2
import pytesseract
import pyttsx3
import logging
import time

def capture_image_with_zed():
    # Run the zed_snap.py script and capture its output
    try:
        result = subprocess.run(['python', 'zed_snap.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        if result.returncode != 0:
            logging.error("Error capturing image with ZED camera: " + result.stderr)
            return None
        return result.stdout.strip()
    except Exception as e:
        logging.error("An error occurred: " + str(e))
        return None

def box_scale_and_ocr_text_in_image(image_path):

    # Initialize pyttsx3 engine
    engine = pyttsx3.init()
    engine.setProperty('rate', 120) # slow down speech
    engine.setProperty('voice', 'english+f3') # set to a "female" voice
    image = cv2.imread(image_path)

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply thresholding
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Sort contours into lines
    lines = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        match_found = False
        for line in lines:
            _, line_y, _, line_h = cv2.boundingRect(line[0])
            if y < line_y + line_h and y + h > line_y:
                line.append(cnt)
                match_found = True
                break
        if not match_found:
            lines.append([cnt])

    logging.info(f"Number of lines detected: {len(lines)}")

    for line in lines:
        line.sort(key=lambda ctr: cv2.boundingRect(ctr)[0])
        for cnt in line:
            x, y, w, h = cv2.boundingRect(cnt)
            # Extract the region of interest (text area)
            roi = image[y:y+h, x:x+w]

            # scale factor 2
            scale_factor = 2
            width = int(roi.shape[1] * scale_factor)
            height = int(roi.shape[0] * scale_factor)
            dim = (width, height)
            resized_roi = cv2.resize(roi, dim, interpolation=cv2.INTER_LINEAR)

            start_time = time.time()
            extracted_text = pytesseract.image_to_string(resized_roi)
            duration = time.time() - start_time
            logging.info(f"OCR processed in {duration:.2f} seconds.")

            # Apply OCR to the scaled text area
            extracted_text = pytesseract.image_to_string(resized_roi)
            print("Extracted Text:", extracted_text)

            # Use pyttsx3 to read the extracted text
            engine.say(extracted_text)
            engine.runAndWait()

    cv2.destroyAllWindows()


# Main function
def main():
    image_path = capture_image_with_zed()
    if image_path:
        box_scale_and_ocr_text_in_image(image_path)
    else:
        logging.info("No image was captured.")
    total_duration = time.time() - start_time
    logging.info(f"Total processing time: {total_duration:.2f} seconds.")

if __name__ == "__main__":
    main()
