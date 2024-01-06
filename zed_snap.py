'''
Copyright (c) 2023 Apollo Timbers. All rights reserved.

This work is licensed under the terms of the Apache License 2.0.
For a copy, see https://github.com/apache/.github/blob/main/LICENSE.

Sophie robot project:

This module brings up the ZED camera and then takes a full resolution image

- Added print out full path and a bit of cleanup 
- Reduced image preview time
- added basic image stabilization 
'''

import sys
import cv2
import numpy as np
import pyzed.sl as sl
from datetime import datetime
import os

# Assuming this is a global variable to store previous frame's features
prev_features = None

def compute_transformation(prev_features, current_features):
    # Calculate the movement (dx, dy) of all matched features
    movements = current_features - prev_features

    # Compute the average movement
    dx, dy = movements.mean(axis=0).flatten()

    # Create an affine transformation matrix for this translation
    transformation_matrix = np.float32([[1, 0, dx], [0, 1, dy]])
    return transformation_matrix

def stabilize_image(current_frame):
    global prev_features
    global prev_frame  # Make sure to also store the previous frame globally

    feature_params = dict(maxCorners=100, qualityLevel=0.3, minDistance=7)
    current_features = cv2.goodFeaturesToTrack(cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY), **feature_params)

    if prev_features is not None and current_features is not None:
        lk_params = dict(winSize=(15, 15), maxLevel=2, criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
        current_features, status, _ = cv2.calcOpticalFlowPyrLK(prev_frame, current_frame, prev_features, None, **lk_params)

        # Filter only good points
        good_new = current_features[status == 1]
        good_old = prev_features[status == 1]

        # Compute the transformation matrix
        transformation_matrix = compute_transformation(good_old, good_new)

        # Apply the transformation to the current frame
        stabilized_frame = cv2.warpAffine(current_frame, transformation_matrix, (current_frame.shape[1], current_frame.shape[0]))

        prev_features = good_new.reshape(-1, 1, 2)
        prev_frame = current_frame.copy()
        return stabilized_frame

    prev_features = current_features
    prev_frame = current_frame.copy()
    return current_frame

def main():
    # Create a ZED camera object
    zed = sl.Camera()

    # Set configuration parameters
    init_params = sl.InitParameters()
    init_params.camera_resolution = sl.RESOLUTION.HD2K  # Set to full resolution, other resolutions sl.RESOLUTION.HD1080 sl.RESOLUTION.HD720
    init_params.depth_mode = sl.DEPTH_MODE.NONE  # Depth not required for this operation

    # Open the camera
    err = zed.open(init_params)
    if err != sl.ERROR_CODE.SUCCESS:
        exit(1)

    # Capture image
    image = sl.Mat()
    if zed.grab() == sl.ERROR_CODE.SUCCESS:
        zed.retrieve_image(image, sl.VIEW.LEFT)  # Retrieve the left image
        image_ocv = image.get_data()  # Convert to OpenCV format

        # Specify the folder to save images
        save_folder = "/home/nvidia/dev/Sophie/Photos"
        os.makedirs(save_folder, exist_ok=True)  # Create the folder if it does not exist

        # Generate a unique filename with date and time
        filename = datetime.now().strftime("%Y%m%d_%H%M%S") + ".png"
        full_path = os.path.join("/home/nvidia/dev/Sophie/Photos", filename)

        # Save the image
        cv2.imwrite(full_path, image_ocv)

        # Display the image
        cv2.imshow("Image", image_ocv)
        cv2.waitKey(2000)  # Wait for 2 seconds (2000 milliseconds)

        # Print the file path before exit
        print(full_path)  # This line is added to output the path of the saved image

        # Clean up
        cv2.destroyAllWindows()
        zed.close()


if __name__ == "__main__":
    main()
