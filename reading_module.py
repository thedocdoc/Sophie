'''
Copyright (c) 2022 Apollo Timbers. All rights reserved.

This work is licensed under the terms of the MIT license.  
For a copy, see <https://opensource.org/licenses/MIT>.

Sophie robot project:

reading physical books/notes module

This reads in a image to OpenCV then does some preprocessing steps to then feeds into pytesseract. Pytesseract then translates the words on the image and prints as a string festival text to speech generator.  
'''
# import opencv
# import opencv
import cv2
#import pytesseract module
import pytesseract
# import offline TTS festival
import os 
 
# Load the input image
image = cv2.imread('intro.jpg')
#cv2.imshow('Original', image)
#cv2.waitKey(0)
 
# Use the cvtColor() function to grayscale the image
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Show grayscale
# cv2.imshow('Grayscale', gray_image)
# cv2.waitKey(0) 

# Median Blur
blur_image = cv2.medianBlur(gray_image, 3)

# Show Median Blur
# cv2.imshow('Median Blur', blur_image)
# cv2.waitKey(0) 

# By default OpenCV stores images in BGR format and since pytesseract assumes RGB format,
# we need to convert from BGR to RGB format/mode:
img_rgb = cv2.cvtColor(blur_image, cv2.COLOR_BGR2RGB)

#Debug pytesseract 
#print(pytesseract.image_to_string(img_rgb))

# Convert read text into speech
os.system('echo "{0}" | festival -b --tts'.format(pytesseract.image_to_string(img_rgb)))         

# Window shown waits for any key pressing event
cv2.destroyAllWindows()
