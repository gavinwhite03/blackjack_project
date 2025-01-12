import cv2
import numpy as np
import os

class TemplateMatcher:
    def match_template(self, region, templates):
        """Match a region with templates using template matching."""
        best_label, best_score = None, 0
        for label, template in templates.items():
            resized_region = cv2.resize(region, (template.shape[1], template.shape[0]))
            result = cv2.matchTemplate(resized_region, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(result)
            if max_val > best_score:
                best_score = max_val
                best_label = label
        return best_label, best_score


# Main execution loop (for testing)
if __name__ == "__main__":
    matcher = TemplateMatcher()
    cap = cv2.VideoCapture(0)  

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
