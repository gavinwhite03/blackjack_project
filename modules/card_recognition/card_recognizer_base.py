import cv2
import os

class CardRecognizerBase:
    def __init__(self, template_dir='/home/gman/blackjack_project/templates/'):
        self.template_dir = template_dir
        self.rank_templates = {}
        self.suit_templates = {}
        self._load_templates()

    def _load_templates(self):
        """Load rank and suit templates."""
        rank_dir = os.path.join(self.template_dir, 'rank')
        suit_dir = os.path.join(self.template_dir, 'suit')

        # Load rank templates
        for filename in os.listdir(rank_dir):
            if filename.endswith('.jpg'):
                rank_name = filename.split('_')[1].split('.')[0]
                template_image = cv2.imread(os.path.join(rank_dir, filename), 0)
                if template_image is not None:
                    self.rank_templates[rank_name] = template_image
                    print(f"[DEBUG] Loaded Rank Template: {rank_name}")

        # Load suit templates
        for filename in os.listdir(suit_dir):
            if filename.endswith('.jpg'):
                suit_name = filename.split('_')[1].split('.')[0]
                template_image = cv2.imread(os.path.join(suit_dir, filename), 0)
                if template_image is not None:
                    self.suit_templates[suit_name] = template_image
                    print(f"[DEBUG] Loaded Suit Template: {suit_name}")

    def preprocess_frame(self, frame):
        """Preprocess the input frame."""
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred_frame = cv2.GaussianBlur(gray_frame, (5, 5), 0)
        threshold_frame = cv2.adaptiveThreshold(
            blurred_frame, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
        )
        return gray_frame, threshold_frame

    def detect_contours(self, threshold_frame):
        """Detect contours in the thresholded frame."""
        contours, _ = cv2.findContours(threshold_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return contours
