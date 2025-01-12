import cv2
import numpy as np
import os
import pytesseract
from modules.card_recognition.card_recognizer_base import CardRecognizerBase

# Set the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'

class ORBCardRecognizer(CardRecognizerBase):
    def __init__(self, good_match_threshold=200, template_size=200, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.good_match_threshold = good_match_threshold
        self.template_size = template_size
        self.orb = cv2.ORB_create()
        self.template_descriptors = {}
        self._compute_descriptors()

    def _compute_descriptors(self):
        """Compute ORB descriptors for templates."""
        for rank, template in self.rank_templates.items():
            if template is None:
                print(f"[ERROR] Failed to load rank template for {rank}")
                continue

            # Resize the template to ensure consistent size
            # resized_template = cv2.resize(template, (100, 100))  # Adjust size as needed
            # kp, des = self.orb.detectAndCompute(resized_template, None)
            template = cv2.resize(template, (self.template_size, self.template_size))
            kp, des = self.orb.detectAndCompute(template, None)
            if des is None:
                print(f"[ERROR] Failed to compute descriptors for rank {rank}")
                cv2.imwrite(f"debug_failed_rank_{rank}.jpg", template)
                continue
            self.template_descriptors[f"rank_{rank}"] = (kp, des)
            print(f"[DEBUG] Computed descriptors for rank {rank}, Keypoints: {len(kp)}, Descriptors Shape: {des.shape}")

        for suit, template in self.suit_templates.items():
            if template is None:
                print(f"[ERROR] Failed to load suit template for {suit}")
                continue

            # Resize the template to ensure consistent size
            template = cv2.resize(template, (self.template_size, self.template_size))
            kp, des = self.orb.detectAndCompute(template, None)
            if des is None:
                print(f"[ERROR] Failed to compute descriptors for suit {suit}")
                continue
            self.template_descriptors[f"suit_{suit}"] = (kp, des)
            print(f"[DEBUG] Computed descriptors for suit {suit}, Keypoints: {len(kp)}, Descriptors Shape: {des.shape}")

    def match_card(self, des_card):
        """Match card descriptors with template descriptors."""
        if des_card is None:
            print("[ERROR] Card descriptors are None.")
            return None, float('inf')

        if des_card.shape[1] != 32:
            print(f"[ERROR] Invalid descriptor size for card: {des_card.shape}. Expected 32 columns.")
            return None, float('inf')

        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        best_label, best_score = None, float('inf')

        for label, (kp_template, des_template) in self.template_descriptors.items():
            if des_template is None:
                print(f"[ERROR] Template descriptors are None for {label}.")
                continue


            matches = bf.match(des_template, des_card)
            if matches:
                score = np.mean([m.distance for m in matches[:10]])
                if score < best_score:
                    best_score = score
                    best_label = label

        print(f"[DEBUG] Best Match: {best_label}, Score: {best_score}")
        return best_label, best_score


    def _ocr_rank_detection(self, roi_top_left):
        """Perform OCR to detect the card rank."""
        ocr_config = '--psm 8 -c tessedit_char_whitelist=AJKQ234567890'
        rank_text = pytesseract.image_to_string(roi_top_left, config=ocr_config).strip()
        # cv2.imshow("ROI", roi_top_left)
        return '10' if rank_text == '0' else rank_text

    def annotate_frame(self, frame, detected_cards):
        """Draw detected cards and labels on the frame."""
        for label, (x, y) in detected_cards:
            cv2.putText(frame, label.replace('_', ' ').title(), (x, y + 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            cv2.rectangle(frame, (x, y), (x + 100, y + 150), (0, 255, 0), 2)
        return frame

    def detect_cards(self, thresh_frame):
        """Detect potential cards using contours and ORB matching."""
        contours, _ = cv2.findContours(thresh_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        detected_cards = []

        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 1000:  # Filter by size
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                if len(approx) == 4:  # Likely a card
                    x, y, w, h = cv2.boundingRect(approx)
                    card_roi = thresh_frame[y:y + h, x:x + w]

                    # Define ROIs for rank and suit
                    rank_roi = card_roi[0:int(h * 0.16), 0:int(w * 0.15)]
                    rank_roi_resized = cv2.resize(rank_roi, (self.template_size, self.template_size))
                    suit_roi = card_roi[int(h * 0.16):int(h * 0.25), 0:int(w * 0.2)]
                    suit_roi_resized = cv2.resize(suit_roi, (self.template_size, self.template_size))
                    detected_rank = self._ocr_rank_detection(rank_roi_resized)
                    detected_suit, suit_score = self.match_card(suit_roi_resized)

                    # Debug: Save or display ROIs
                    # cv2.imshow("Rank ROI", rank_roi)
                    # cv2.imshow("Suit ROI", suit_roi)
                    cv2.waitKey(0)
                    cv2.destroyAllWindows()

                    detected_cards.append({"rank_roi": detected_rank, "suit_roi": detected_suit, "position": (x, y)})

        return detected_cards

def detect_cards(self, gray_frame, thresh_frame):
    """
    Detect the card using preprocessed frames.
    Args:
        gray_frame (numpy.ndarray): Grayscale frame.
        thresh_frame (numpy.ndarray): Thresholded frame.
    Returns:
        dict: Detected card with rank and suit.
    """
    detected_cards = self.detect_cards(gray_frame, thresh_frame)
    return detected_cards[0] if detected_cards else {"rank": None, "suit": None}


