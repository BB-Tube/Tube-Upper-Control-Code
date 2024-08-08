import cv2
import numpy as np
from enum import Enum
from util import Ball

import cv2
import numpy as np
import datetime
import os
import atexit
import time
from collections import Counter

# Define the subfolder where you want to save the photos
save_directory = os.path.join(os.getcwd(), "captured_images")
os.makedirs(save_directory, exist_ok=True)

# Define the filename with timestamp
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
filename = os.path.join(save_directory, f"photo_{timestamp}.jpg")
output_filename = os.path.join(save_directory, f"output_{timestamp}.jpg")

class ColorSensor(object):
    def __init__(self):
        self.cap = cv2.VideoCapture(0)  # 0 is usually the default camera
        self.kill_cam()
        self.setup_cam()
        atexit.register(self.kill_cam)

    def kill_cam(self):
        # Release the camera
        self.cap.release()

        # Close all OpenCV windows
        cv2.destroyAllWindows()

    def setup_cam(self):
        # Initialize the camera
        self.cap = cv2.VideoCapture(0)  # 0 is usually the default camera

    def get_ball_color(self):
        # Check if the camera opened successfully
        if not self.cap.isOpened():
            print("Error: Could not open camera.")
            return
        # Capture a single frame
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        ret, frame = self.cap.read()
        if not ret:
            print("Error: Failed to capture image.")
            return
        # Crop the image (example: crop from (x1, y1) to (x2, y2))
        x1, y1 = 150, 150  # Start pixel coordinates
        x2, y2 = 400, 450  # End pixel coordinates
        cropped_image = frame[y1:y2, x1:x2]

        # Convert cropped image to grayscale
        gray_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
        # Optional: Increase contrast
        # You can adjust alpha (contrast) and beta (brightness) to improve visibility
        alpha = 1.5  # Contrast control
        beta = 20    # Brightness control
        contrasted_image = cv2.convertScaleAbs(gray_image, alpha=alpha, beta=beta)
        # Apply Gaussian Blur
        blurred_image = cv2.GaussianBlur(contrasted_image, (9, 9), 0)

        # Detect circles in the cropped image
        circles = cv2.HoughCircles(contrasted_image, cv2.HOUGH_GRADIENT, 1, 100,
                                param1=50, param2=30, minRadius=60, maxRadius=80)

        votes = []
        if circles is not None:
            circles = np.uint16(np.around(circles))
            # print(f"Detected {len(circles[0, :])} circle(s)")

            for i in circles[0, :]:
                center_x, center_y, radius = i[0], i[1], i[2]
                mask = np.zeros_like(gray_image)
                cv2.circle(mask, (center_x, center_y), radius, (255, 255, 255), -1)

                # Calculate average pixel intensity within the circle
                masked_img = cv2.bitwise_and(gray_image, gray_image, mask=mask)
                mean_val = cv2.mean(masked_img, mask=mask)[0]

                # Select the circle color based on the average intensity
                if mean_val > 127:  # Predominantly white
                    circle_color = (0, 0, 255)  # Red color in BGR
                    votes.append(Ball.WHITE)
                    # print("The circle is predominantly white.")
                else:
                    circle_color = (0, 255, 0)  # Green color in BGR
                    votes.append(Ball.BLACK)
                    # print("The circle is predominantly black.")

                # Draw the circle in the chosen color
                cv2.circle(blurred_image, (center_x, center_y), radius, circle_color, 2)

            # Display the image with the colored circles
            # Save the cropped image
        else:
            pass
            # print("No circles detected.")

        # Define the filename with timestamp
        filename = os.path.join(save_directory, f"photo_{timestamp}.jpg")
        output_filename = os.path.join(save_directory, f"output_{timestamp}.jpg")
        cv2.imwrite(output_filename, blurred_image)
        print("writing")
        
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        # print("Votes : ", votes)

        occurance_count = Counter(votes)
        if not votes:
            return Ball.NONE
            ### should be Ball.NONE, but am recieving too many false positives as none when the ball is white
        return occurance_count.most_common(1)[0][0]

if __name__ == "__main__":
    cs = ColorSensor()
    do_times = 100
    tic = time.time()
    for i in range(do_times):
        print()
        print(cs.get_ball_color())
    toc = time.time()
    print((toc-tic)/do_times)


