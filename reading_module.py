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
- Sort the words form left to right, and top to bottom
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
    engine.setProperty('rate', 120)  # slow down speech
    engine.setProperty('voice', 'english+f3')  # set to a "female" voice
    image = cv2.imread(image_path)

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply thresholding
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Organize contours into lines and sort them
    lines = {}
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        line_index = y // 10  # assuming a fixed line height, adjust as needed
        if line_index not in lines:
            lines[line_index] = []
        lines[line_index].append((x, cnt))

    # Logging the number of lines detected
    logging.info(f"Number of lines detected: {len(lines)}")

    # Process each line
    for _, line_contours in sorted(lines.items()):
        # Sort contours in a line based on the x position
        sorted_contours = sorted(line_contours, key=lambda item: item[0])
        for x, cnt in sorted_contours:
            _, y, w, h = cv2.boundingRect(cnt)
            # Extract the region of interest (text area)
            roi = image[y:y+h, x:x+w]

            # scale factor 2
            scale_factor = 2
            width = int(roi.shape[1] * scale_factor)
            height = int(roi.shape[0] * scale_factor)
            dim = (width, height)
            resized_roi = cv2.resize(roi, dim, interpolation=cv2.INTER_LINEAR)

            # Measure time for OCR
            start_time = time.time()
            extracted_text = pytesseract.image_to_string(resized_roi)
            duration = time.time() - start_time
            logging.info(f"OCR processed in {duration:.2f} seconds.")

            # Print and read the extracted text
            print("Extracted Text:", extracted_text)
            engine.say(extracted_text)
            engine.runAndWait()

    # Release all resources
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
