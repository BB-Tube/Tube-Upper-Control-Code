import cv2
import numpy as np
import datetime
import os

### 

# Define the subfolder where you want to save the photos
save_directory = os.path.join(os.getcwd(), "captured_images")
os.makedirs(save_directory, exist_ok=True)

# Define the filename with timestamp
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
filename = os.path.join(save_directory, f"photo_{timestamp}.jpg")
output_filename = os.path.join(save_directory, f"output_{timestamp}.jpg")

# Capture the image from the camera
cap = cv2.VideoCapture(0)  # 0 is the default camera
ret, frame = cap.read()
cap.release()

# Check if the image was captured
if not ret:
    print("Failed to capture image")
    exit()

# Convert the image to grayscale (since it's already black and white, this is redundant but ensures correct format)
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

# Apply Gaussian blur to the grayscale image
blurred = cv2.GaussianBlur(gray, (15, 15), 0)

# Detect circles in the image using HoughCircles
circles = cv2.HoughCircles(
    blurred, 
    cv2.HOUGH_GRADIENT, 
    dp=1.2, 
    minDist=50, 
    param1=50, 
    param2=30, 
    minRadius=gray.shape[0] // 12,  # min radius based on vertical height
    maxRadius=gray.shape[0] // 3    # max radius based on vertical height
)

# Process the detected circles
if circles is not None:
    circles = np.round(circles[0, :]).astype("int")

    for (x, y, r) in circles:
        # Extract the ROI for the circle
        roi = gray[y-r:y+r, x-r:x+r]

        # Calculate the mean pixel value
        mean_val = np.mean(roi)

        # Determine if the ball is black or white based on the mean pixel value
        if mean_val > 128:  # threshold can be adjusted based on lighting conditions
            color = (0, 0, 255)  # Red for white ball
        else:
            color = (0, 255, 0)  # Green for black ball

        # Draw a rectangle around the detected ball
        cv2.rectangle(frame, (x-r, y-r), (x+r, y+r), color, 2)

# Save the original image and the processed image
cv2.imwrite(filename, gray)
cv2.imwrite(output_filename, frame)

print(f"Images saved to {filename} and {output_filename}")
