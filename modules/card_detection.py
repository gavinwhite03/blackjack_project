import cv2
import numpy as np
import pytesseract
from collections import Counter

def normalize_card_rank(rank):
    """
    Normalize card rank for consistent representation.
    :param rank: Detected rank from OCR (e.g., 'A', '10', 'J').
    :return: Normalized rank (e.g., 'Ace', '10', 'Jack').
    """
    rank_mapping = {
        'A': 'Ace',
        'J': 'Jack',
        'Q': 'Queen',
        'K': 'King'
    }
    return rank_mapping.get(rank, rank)


class DetectCards:
    @staticmethod
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

    @staticmethod
    def extract_rank_using_ocr(image, attempts=3):
        """Run OCR multiple times and return the most frequent result."""
        ocr_config = "--psm 10 -c tessedit_char_whitelist=023456789JQKA"
        results = []

        for _ in range(attempts):
            rank_text = pytesseract.image_to_string(image, config=ocr_config).strip()
            if rank_text:
                results.append(rank_text)
        
        if results:
            most_common = Counter(results).most_common(1)
            if most_common == '0':
                most_common = '10'
            return most_common[0][0]  
        return None

    @staticmethod
    def detect_in_roi(name, roi):
        """
        Detect cards in a given ROI.
        :param name: Name of the ROI (e.g., 'Dealer', 'Player 1').
        :param roi: The region of interest.
        :return: Tuple containing the ROI name and a list of detected cards.
        """
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
                    warped_card = DetectCards.flattener(roi, approx, w, h)

                    # Extract rank region
                    corner_width = int(warped_card.shape[1] * 0.15)
                    corner_height = int(warped_card.shape[0] * 0.32)
                    rank_region = warped_card[:corner_height // 2, :corner_width]

                    # OCR for rank detection
                    detected_rank = DetectCards.extract_rank_using_ocr(rank_region)
                    if detected_rank:
                        normalized_rank = normalize_card_rank(detected_rank)
                        detected_ranks.append(normalized_rank)

        return name, detected_ranks
