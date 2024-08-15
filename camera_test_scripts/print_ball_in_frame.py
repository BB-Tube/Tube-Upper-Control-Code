import os
import time
from picamera2 import Picamera2
import cv2
import numpy as np

# Create a folder called 'captured_images' if it doesn't exist
folder_name = 'captured_images'
if not os.path.exists(folder_name):
    os.makedirs(folder_name)

# Initialize the camera
camera = Picamera2()

# Configure the camera with very low resolution for maximum frequency and set frame rate
camera.configure(camera.create_still_configuration(main={"size": (320, 240)}, controls={"FrameRate": 90}))

# Start the camera
camera.start()

# Capture images at the highest frequency and save every 100th frame
capture_count = 0
save_count = 0
capture_duration = 5  # capture for 5 seconds
start_time = time.time()

doPhoto = True

frame = camera.capture_array()  # Capture the image into memory
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

circles = cv2.HoughCircles(
    gray, 
    cv2.HOUGH_GRADIENT, 
    dp=1, 
    minDist=100, 
    param1=50, 
    param2=30, 
    minRadius=75, 
    maxRadius=100
)

# If some circles are detected, process them
if circles is not None:
    circles = np.uint16(np.around(circles))
    for i in circles[0, :]:
        x, y, radius = i[0], i[1], i[2]

        # Print the position and radius of the circle
        print(f"Circle at (x: {x}, y: {y}), Radius: {radius}")

        # Create a mask to extract the circle
        mask = np.zeros_like(gray)
        cv2.circle(mask, (x, y), radius, 255, thickness=-1)

        # Extract the circle from the original frame
        masked_image = cv2.bitwise_and(frame, frame, mask=mask)

        # Get the pixels inside the circle
        circle_pixels = masked_image[np.where(mask == 255)]

        # Calculate the median color in the circle
        median_color = np.median(circle_pixels, axis=0)

        # Print the median color
        print(f"Median Color in Circle (BGR): {median_color}")

        # Draw the circle and center on the frame for visualization
        cv2.circle(frame, (x, y), radius, (0, 255, 0), 2)
        cv2.circle(frame, (x, y), 2, (0, 0, 255), 3)