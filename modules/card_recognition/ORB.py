import cv2
import numpy as np
import os
import pytesseract

# Set the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'

class ORBCardRecognizer:
    def __init__(self, card_images_directory='/home/gman/blackjack_project/tests/test_dataset', good_match_threshold=200):
        self.card_images_directory = card_images_directory
        self.good_match_threshold = good_match_threshold
        self.template_images = {}
        self.template_descriptors = {}
        self.orb = cv2.ORB_create()
        self._load_templates()

    def _load_templates(self):
        """Load card templates and compute descriptors."""
        for filename in os.listdir(self.card_images_directory):
            if filename.endswith('.jpg'):
                card_name_parts = filename[:-4].split(' of ')
                if len(card_name_parts) == 2:
                    rank, suit = card_name_parts
                    key = f"{rank.lower()}_{suit.lower()}"
                    template_image = cv2.imread(
                        os.path.join(self.card_images_directory, filename), 0
                    )
                    if template_image is not None:
                        self.template_images[key] = template_image
                        kp, des = self.orb.detectAndCompute(template_image, None)
                        self.template_descriptors[key] = (kp, des)
                        print(f"Loaded Templates: {list(self.template_descriptors.keys())}")

    def preprocess_frame(self, frame):
        """Preprocess frame (resize, grayscale, threshold)."""
        resized_frame = cv2.resize(frame, None, fx=0.5, fy=0.5)
        gray_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)
        blurred_frame = cv2.GaussianBlur(gray_frame, (5, 5), 0)
        thresh_frame = cv2.adaptiveThreshold(
            blurred_frame, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
        )
        return gray_frame, thresh_frame

    def detect_cards(self, gray_frame, thresh_frame):
        """Detect potential cards using contours and ORB matching."""
        contours, _ = cv2.findContours(thresh_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        detected_cards = []
        cv2.drawKeypoints(self.test_img, self.test_kp, self.test_img, color=(0, 255, 0))
        cv2.imwrite(f"debug_keypoints_test.jpg", self.test_img)

        for label, (kp_template, _) in self.template_descriptors.items():
        template_img = self.template_images[label]
        cv2.drawKeypoints(template_img, kp_template, template_img, color=(255, 0, 0))
        cv2.imwrite(f"debug_keypoints_template_{label}.jpg", template_img)

        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 1000:
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                if len(approx) == 4:
                    x, y, w, h = cv2.boundingRect(approx)
                    card_roi = gray_frame[y:y + h, x:x + w]
                    kp_card, des_card = self.orb.detectAndCompute(card_roi, None)
                    self.test_img = card_roi
                    self.test_kp = kp_card
                    print(f"[DEBUG] Keypoints in Card ROI: {len(kp_card) if kp_card else 0}, Descriptors: {des_card.shape if des_card is not None else 'None'}")

                    if des_card is not None:
                        best_match_label, best_match_score = self._match_card(des_card)
                        if best_match_label and best_match_score < self.good_match_threshold:
                            roi_top_left = card_roi[0:int(h * 0.15), 0:int(w * 0.15)]
                            rank_text = self._ocr_rank_detection(roi_top_left)
                            detected_label = f"{rank_text} {best_match_label.split('_')[1]}"
                            detected_cards.append((detected_label, (x, y)))

        return detected_cards

    def _match_card(self, des_card):
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        best_match_label = None
        best_match_score = float('inf')

        for label, (kp_template, des_template) in self.template_descriptors.items():
            if des_template is None:
                print(f"[DEBUG] Template {label} has no descriptors.")
                continue
            
            if des_card is None:
                print("[DEBUG] Test image descriptors are None.")
                return None, float('inf')
            
            matches = bf.match(des_template, des_card)
            print(f"[DEBUG] Matches for {label}: {len(matches)}")

            if des_template is not None:
                # Match descriptors
                matches = bf.match(des_template, des_card)
                matches = sorted(matches, key=lambda x: x.distance)
                print(f"[DEBUG] Matches for {label}: {len(matches)}, Match Distances: {[m.distance for m in matches[:5]]}")

                # Save visualization of matches for debugging
                if len(matches) > 0:
                    template_img = self.template_images[label]
                    # Draw keypoints and matches
                    match_img = cv2.drawMatches(
                        template_img, kp_template, self.test_img, self.test_kp, matches[:10], None, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS
                    )
                    cv2.imshow("Matches", match_img)
                    cv2.waitKey(0)
                    cv2.destroyAllWindows()

                # Compute match score
                if matches and len(matches) > 0:
                    match_score = np.mean([m.distance for m in matches[:10]])
                    if match_score < best_match_score:
                        best_match_score = match_score
                        best_match_label = label

        print(f"[DEBUG] Best Match: {best_match_label}, Score: {best_match_score}")
        return best_match_label, best_match_score

    def _ocr_rank_detection(self, roi_top_left):
        """Perform OCR to detect the card rank."""
        ocr_config = '--psm 8 -c tessedit_char_whitelist=AJKQ234567890'
        rank_text = pytesseract.image_to_string(roi_top_left, config=ocr_config).strip()
        return '10' if rank_text == '0' else rank_text

    def annotate_frame(self, frame, detected_cards):
        """Draw detected cards and labels on the frame."""
        for label, (x, y) in detected_cards:
            cv2.putText(frame, label.replace('_', ' ').title(), (x, y + 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            cv2.rectangle(frame, (x, y), (x + 100, y + 150), (0, 255, 0), 2)
        return frame

    
def detect_card(image):
    recognizer = ORBCardRecognizer()
    gray_frame, thresh_frame = recognizer.preprocess_frame(image)
    detected_cards = recognizer.detect_cards(gray_frame, thresh_frame)
    return detected_cards[0] if detected_cards else {"rank": None, "suit": None}
