from picamera2 import Picamera2
import libcamera
import cv2

print(libcamera.__version__)
def test_camera():
    # Initialize the camera
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)})
    picam2.configure(config)
    picam2.start()

    print("Camera initialized. Press 'q' to quit.")
    while True:
        # Capture a frame
        frame = picam2.capture_array()

        # Display the frame using OpenCV
        cv2.imshow("Camera Preview", frame)

        # Exit on pressing 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Stop the camera and clean up
    picam2.stop()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    test_camera()
