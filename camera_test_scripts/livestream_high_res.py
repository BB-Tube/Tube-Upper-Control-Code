import time
from picamera2 import Picamera2, Preview

# Initialize the camera
camera = Picamera2()

# Configure the camera for video stream with high resolution and 30 FPS
camera_config = camera.create_preview_configuration(main={"size": (1920, 1080)})
camera.configure(camera_config)

# Set the frame rate to 30 FPS
camera.set_controls({"FrameRate": 30})

# Start the camera with preview
camera.start_preview(Preview.QTGL)  # Use QTGL for OpenGL rendering

# Start the camera
camera.start()

# Display the video stream for 10 seconds
time.sleep(1000)

# Stop the camera
camera.stop_preview()
camera.stop()
