from picamera2 import Picamera2
import cv2
from card_recognition.card_pipline import recognize_card

def capture_and_recognize():
    # Initialize the camera
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)})
    picam2.configure(config)
    picam2.start()

    print("Camera initialized. Press 'q' to quit.")
    while True:
        # Capture a frame
        frame = picam2.capture_array()

        # Convert to BGR for OpenCV compatibility
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # Pass the frame to the card recognition pipeline
        result = recognize_card(frame_bgr)
        print(f"Detected Card: {result}")

        # Annotate the frame
        if result["rank"] and result["suit"]:
            cv2.putText(frame_bgr, f"{result['rank']} of {result['suit']}",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Display the frame
        cv2.imshow("Card Recognition", frame_bgr)

        # Exit on pressing 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Stop the camera and clean up
    picam2.stop()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    capture_and_recognize()
