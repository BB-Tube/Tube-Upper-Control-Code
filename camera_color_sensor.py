import os
import time
from picamera2 import Picamera2
import cv2
import numpy as np
import sys

# Add the parent directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from util import *

# Initialize the camera

class CCS_VARIABLE():
    BALL_X = 158
    BALL_Y = 146

class CameraColorSensor(object):
    def __init__(self):
        self.camera = Picamera2()

        # Configure the camera with very low resolution for maximum frequency and set frame rate
        self.camera.configure(self.camera.create_still_configuration(main={"size": (320, 240)}, controls={"FrameRate": 90}))
        self.camera.start()

        self.frame = None

    def take_frame(self):
        self.frame = self.camera.capture_array()  # Capture the image into memory

    def read_color_vals(self):
        self.take_frame()
        gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)

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

        circles_colors = []

        # If some circles are detected, process them
        if circles is not None:
            circles = np.uint16(np.around(circles))
            for i in circles[0, :]:
                x, y, radius = i[0], i[1], i[2]

                # Print the position and radius of the circle
                # print(f"Circle at (x: {x}, y: {y}), Radius: {radius}")

                # Create a mask to extract the circle
                mask = np.zeros_like(gray)
                cv2.circle(mask, (x, y), radius, 255, thickness=-1)

                # Extract the circle from the original frame
                masked_image = cv2.bitwise_and(self.frame, self.frame, mask=mask)

                # Get the pixels inside the circle
                circle_pixels = masked_image[np.where(mask == 255)]

                # Calculate the median color in the circle
                median_color = np.median(circle_pixels, axis=0)

                circles_colors.append([x,y,radius,median_color])

                # Print the median color
                # print(f"Median Color in Circle (BGR): {median_color}")
            # print(circles_colors)
        
        min_delta = 320+240
        color_closest_ball = [None, None, None]
        for i in circles_colors:
            delta = abs(i[0] - CCS_VARIABLE.BALL_X) + abs(i[1] - CCS_VARIABLE.BALL_Y)
            if delta < min_delta:
                min_delta = delta
                color_closest_ball = i[-1]
        return color_closest_ball

    def get_ball_color(self):
        read_b, read_r, read_g = self.read_color_vals()
        if read_b is None:
            return Ball.NONE
        
        closest = 255 ** 3
        closest_ball = None
        for ball in BALL_COLOR:
            ball_b, ball_r, ball_g = BALL_COLOR[ball]
            dist = abs(ball_b - read_b) + abs(ball_g - read_g) + abs(ball_r - read_r)
            if dist < closest:
                closest = dist
                closest_ball = ball
        return closest_ball
        
if __name__ == '__main__':
    ccs = CameraColorSensor()
    # print(ccs.read_color_vals())
    iterator = 0
    while True:
        print()
        print(ccs.get_ball_color())
        print(iterator)
        iterator += 1