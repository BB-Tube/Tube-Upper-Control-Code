import time
from picamera2 import Picamera2, Preview

# Initialize the camera
camera = Picamera2()

# Configure the camera for video stream with low resolution and high frame rate
camera_config = camera.create_preview_configuration(main={"size": (640, 480)})
camera.configure(camera_config)

# Set the frame rate to 90 Hz
camera.set_controls({"FrameRate": 90})

# Start the camera with preview
camera.start_preview(Preview.QTGL)  # Use QTGL for OpenGL rendering, suitable for high frame rates

# Start the camera
camera.start()

# Display the video stream for 10 seconds
time.sleep(1000)

# Stop the camera
camera.stop_preview()
camera.stop()
