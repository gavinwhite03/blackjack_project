import cv2
import numpy as np
import os

class TemplateMatcher:
    def __init__(self, card_img_folder='processed_dataset/thresholded/cropped'):
        self.card_img_folder = card_img_folder
        self.rank_templates = {}
        self.suit_templates = {}
        self._load_templates()

    def _load_templates(self):
        """Load rank and suit templates from the folder."""
        for filename in os.listdir(self.card_img_folder):
            file_path = os.path.join(self.card_img_folder, filename)
            img = cv2.imread(file_path, 0)
            if img is None:
                print(f"Failed to load image {filename}")
                continue

            if "rank_" in filename:
                rank = filename.split('_')[1].split('.')[0]
                self.rank_templates[rank] = img
            elif "suit_" in filename:
                suit = filename.split('_')[1].split('.')[0]
                self.suit_templates[suit] = img

    def preprocess_frame(self, frame):
        """Preprocess the input frame."""
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred_frame = cv2.GaussianBlur(gray_frame, (11, 11), 0)
        threshold_frame = cv2.adaptiveThreshold(
            blurred_frame, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
        )
        kernel = np.ones((5, 5), np.uint8)
        morph_frame = cv2.morphologyEx(threshold_frame, cv2.MORPH_CLOSE, kernel)
        return gray_frame, morph_frame

    def detect_cards(self, frame):
        """Detect cards and identify their rank and suit."""
        gray_frame, threshold_frame = self.preprocess_frame(frame)
        edges = cv2.Canny(threshold_frame, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        detected_cards = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 1000:
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                if len(approx) == 4:
                    x, y, w, h = cv2.boundingRect(approx)
                    top_left_corner = frame[y:y + int(h * 0.3), x:x + int(w * 0.15)]
                    rank, suit = self._identify_rank_and_suit(top_left_corner)
                    if rank and suit:
                        detected_cards.append({"rank": rank, "suit": suit, "position": (x, y)})
        return detected_cards

    def _identify_rank_and_suit(self, top_left_corner):
        """Identify the rank and suit of the card."""
        corner_height, corner_width = top_left_corner.shape[:2]
        rank_region = top_left_corner[0:int(corner_height * 0.5), :]
        suit_region = top_left_corner[int(corner_height * 0.5):, :]

        rank = self._match_template(rank_region, self.rank_templates)
        suit = self._match_template(suit_region, self.suit_templates)
        return rank, suit

    def _match_template(self, region, templates):
        """Match a region with templates using template matching."""
        best_match = None
        best_score = 0
        for label, template in templates.items():
            resized_region = cv2.resize(region, (template.shape[1], template.shape[0]))
            result = cv2.matchTemplate(resized_region, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(result)
            if max_val > best_score:
                best_score = max_val
                best_match = label
        return best_match

    def annotate_frame(self, frame, detected_cards):
        """Annotate the frame with detected card labels."""
        for card in detected_cards:
            rank, suit, (x, y) = card["rank"], card["suit"], card["position"]
            label = f"{rank} of {suit}"
            cv2.rectangle(frame, (x, y), (x + 100, y + 150), (0, 255, 0), 2)
            cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
        return frame

# Main execution loop (for testing)
if __name__ == "__main__":
    matcher = TemplateMatcher()
    cap = cv2.VideoCapture(0)  # Adjust camera index as needed

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame.")
            break

        detected_cards = matcher.detect_cards(frame)
        annotated_frame = matcher.annotate_frame(frame, detected_cards)

        cv2.imshow('Card Detection', annotated_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
