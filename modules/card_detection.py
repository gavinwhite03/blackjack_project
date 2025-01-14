import cv2
import numpy as np
import pytesseract
from collections import Counter
from modules.cloud_integration import init_firebase, update_player_cards

class DetectCards():
    # Flatten function
    def flattener(image, pts, w, h):
        temp_rect = np.zeros((4, 2), dtype="float32")
    
        s = np.sum(pts, axis=2)
        tl = pts[np.argmin(s)]
        br = pts[np.argmax(s)]

        diff = np.diff(pts, axis=-1)
        tr = pts[np.argmin(diff)]
        bl = pts[np.argmax(diff)]

        if w <= 0.8 * h:  # Vertical orientation
            temp_rect[0] = tl
            temp_rect[1] = tr
            temp_rect[2] = br
            temp_rect[3] = bl
        elif w >= 1.2 * h:  # Horizontal orientation
            temp_rect[0] = bl
            temp_rect[1] = tl
            temp_rect[2] = tr
            temp_rect[3] = br
        else:  # Diamond orientation
            if pts[1][0][1] <= pts[3][0][1]:  # Tilted left
                temp_rect[0] = pts[1][0]
                temp_rect[1] = pts[0][0]
                temp_rect[2] = pts[3][0]
                temp_rect[3] = pts[2][0]
            else:  # Tilted right
                temp_rect[0] = pts[0][0]
                temp_rect[1] = pts[3][0]
                temp_rect[2] = pts[2][0]
                temp_rect[3] = pts[1][0]

        maxWidth = 200
        maxHeight = 300
        dst = np.array([[0, 0], [maxWidth - 1, 0], [maxWidth - 1, maxHeight - 1], [0, maxHeight - 1]], np.float32)
        M = cv2.getPerspectiveTransform(temp_rect, dst)
        warp = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
        warp = cv2.cvtColor(warp, cv2.COLOR_BGR2GRAY)
        warp = cv2.adaptiveThreshold(warp, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
        return warp

    def extract_rank_using_ocr(image, attempts=3):
        """Run OCR multiple times and return the most frequent result."""
        ocr_config = "--psm 10 -c tessedit_char_whitelist=23456789JQKA"
        results = []

        for _ in range(attempts):
            rank_text = pytesseract.image_to_string(image, config=ocr_config).strip()
            if rank_text:
                results.append(rank_text)

        # Count occurrences of each result and choose the most common one
        if results:
            most_common = Counter(results).most_common(1)
            return most_common[0][0]  # Return the most common rank
        return None

    # Initialize webcam
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture image.")
            break

        # Get frame dimensions
        height, width, _ = frame.shape

        # Define ROIs
        dealer_roi = frame[:height // 2, :]  # Top half
        player1_roi = frame[height // 2:, :width // 2]  # Bottom left
        player2_roi = frame[height // 2:, width // 2:]  # Bottom right

        # Define a list of ROIs for processing
        rois = [
            ("Dealer", dealer_roi),
            ("Player 1", player1_roi),
            ("Player 2", player2_roi)
        ]

        # Wait for the 'p' key
        key = cv2.waitKey(1) & 0xFF
        if key == ord('p'):
            for name, roi in rois:
                gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                blurred_roi = cv2.GaussianBlur(gray_roi, (11, 11), 0)
                threshold_roi = cv2.adaptiveThreshold(blurred_roi, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
                kernel = np.ones((5, 5), np.uint8)
                morph_roi = cv2.morphologyEx(threshold_roi, cv2.MORPH_CLOSE, kernel)
                edges_roi = cv2.Canny(morph_roi, 50, 150)

                contours, _ = cv2.findContours(edges_roi, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                detected_ranks = []

                for contour in contours:
                    area = cv2.contourArea(contour)
                
                    if area > 1300:
                        epsilon = 0.02 * cv2.arcLength(contour, True)
                        approx = cv2.approxPolyDP(contour, epsilon, True)

                        if len(approx) == 4:  # Likely a card
                            x, y, w, h = cv2.boundingRect(contour)
                            warped_card = flattener(roi, approx, w, h)

                            # Extract rank region
                            corner_width = int(warped_card.shape[1] * 0.15)
                            corner_height = int(warped_card.shape[0] * 0.32)
                            rank_region = warped_card[:corner_height // 2, :corner_width]

                            # OCR for rank detection
                            detected_rank = extract_rank_using_ocr(rank_region)
                            if detected_rank:
                                detected_ranks.append(detected_rank)

                            # Display rank on the ROI
                            if detected_rank:
                                cv2.putText(roi, detected_rank, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                # Update Firebase for each player
                optimal_action = "Stand"  # Replace with your Blackjack strategy logic
                update_player_cards(name, detected_ranks, optimal_action)

                print(f"{name} Detected Ranks: {detected_ranks}")

        # Display ROIs
        cv2.imshow('Dealer ROI', dealer_roi)
        cv2.imshow('Player 1 ROI', player1_roi)
        cv2.imshow('Player 2 ROI', player2_roi)

        # Exit on pressing 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the capture and close windows
    cap.release()
    cv2.destroyAllWindows()

