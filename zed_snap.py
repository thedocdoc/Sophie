'''
Copyright (c) 2023 Apollo Timbers. All rights reserved.

This work is licensed under the terms of the MIT license.  
For a copy, see <https://opensource.org/licenses/MIT>.

Sophie robot project:

This module brings up teh ZED camera and then takes a full resolution image

- Added print out full path and a bit of cleanup 
'''

import sys
import pyzed.sl as sl
import cv2
from datetime import datetime
import os

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
        cv2.waitKey(6000)  # Wait for 6 seconds (6000 milliseconds)

        # Print the file path before exit
        print(full_path)  # This line is added to output the path of the saved image

        # Clean up
        cv2.destroyAllWindows()
        zed.close()


if __name__ == "__main__":
    main()
