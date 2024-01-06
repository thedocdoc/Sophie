'''
Copyright (c) 2022 Apollo Timbers. All rights reserved.

This work is licensed under the terms of the Apache License 2.0.
For a copy, see https://github.com/apache/.github/blob/main/LICENSE.

Sophie robot project:
Reading physical books/notes module.

This reads in an image from the ZED camera to OpenCV, then performs some preprocessing steps and feeds it into pytesseract. Pytesseract then translates the words on the image and prints as a string for Python TTS. This allows the robot to read text put in front of it, working well with black text on a white background.

- Added getting an image from the ZED.
- Changed to Python text-to-speech.
- Heavily modified the pipeline to scale the image and box the text to help OCR be faster and more accurate, it also aranges teh bounding boxes from left to right and top to bottom so that it reads in teh correct order.
- You need to hold the boox ~12 inches from the camera, this may be improved by upping the scale factor but it is working well at that distance for now.
- More optimization is needed in the pipeline...
'''

import subprocess
import cv2
import pytesseract
import pyttsx3
import logging
import time

# Configure logging for debugging and performance monitoring
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def capture_image_with_zed():
    # Capture an image using the ZED camera
    try:
        logging.info("Capturing image with ZED camera.")
        start_time = time.time()
        result = subprocess.run(['python', 'zed_snap.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        duration = time.time() - start_time
        logging.info(f"Image captured in {duration:.2f} seconds.")
        if result.returncode != 0:
            logging.error("Error capturing image with ZED camera: " + result.stderr)
            return None
        return result.stdout.strip()
    except Exception as e:
        logging.error("An error occurred: " + str(e))
        return None

def box_scale_and_ocr_text_in_image(image_path):
    # Initialize text-to-speech engine
    engine = pyttsx3.init()
    engine.setProperty('rate', 120)
    engine.setProperty('voice', 'english+f3')
    image = cv2.imread(image_path)

    # Convert image to grayscale and apply thresholding for contour detection
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Group detected contours into lines of text
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

    # Process each line and contour for OCR
    for line in lines:
        line.sort(key=lambda ctr: cv2.boundingRect(ctr)[0])
        for cnt in line:
            x, y, w, h = cv2.boundingRect(cnt)
            roi = image[y:y+h, x:x+w]

            # Scale the region of interest
            scale_factor = 2
            width = int(roi.shape[1] * scale_factor)
            height = int(roi.shape[0] * scale_factor)
            dim = (width, height)
            resized_roi = cv2.resize(roi, dim, interpolation=cv2.INTER_LINEAR)

            # Apply OCR and measure processing time
            start_time = time.time()
            extracted_text = pytesseract.image_to_string(resized_roi)
            duration = time.time() - start_time
            logging.info(f"OCR processed in {duration:.2f} seconds.")

            # Output and speak the extracted text
            print("Extracted Text:", extracted_text)
            engine.say(extracted_text)
            engine.runAndWait()

    cv2.destroyAllWindows()

def main():
    # Measure total processing time
    start_time = time.time()
    image_path = capture_image_with_zed()
    if image_path:
        box_scale_and_ocr_text_in_image(image_path)
    else:
        logging.info("No image was captured.")
    total_duration = time.time() - start_time
    logging.info(f"Total processing time: {total_duration:.2f} seconds.")

if __name__ == "__main__":
    main()
