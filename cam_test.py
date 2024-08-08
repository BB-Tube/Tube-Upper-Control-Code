import cv2

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open video device.")
else:
    # Set resolution to a lower value
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    # Try setting a higher frame rate
    cap.set(cv2.CAP_PROP_FPS, 120)
    actual_fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"Attempted to set frame rate to 120 FPS, actual frame rate: {actual_fps} FPS")

    cap.release()
