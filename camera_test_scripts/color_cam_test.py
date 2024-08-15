import os
import time
from picamera2 import Picamera2

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

while time.time() - start_time < capture_duration:
    capture_count += 1
    frame = camera.capture_array()  # Capture the image into memory

    # Save every 100th frame
    if doPhoto:
        timestamp = time.strftime("%Y%m%d-%H%M%S_%f")
        image_path = os.path.join(folder_name, f'image_{timestamp}.jpg')
        camera.capture_file(image_path)
        doPhoto = False

end_time = time.time()

# Stop the camera
camera.stop()

# Calculate and print the capture frequency
capture_frequency = capture_count / (end_time - start_time)
print(f"Captured {capture_count} images in {end_time - start_time:.2f} seconds")
print(f"Capture frequency: {capture_frequency:.2f} frames per second")
print(f"Saved {save_count} images")
