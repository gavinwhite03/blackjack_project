from modules.card_recognition.ORB import ORBCardRecognizer
from modules.card_recognition.template_matching import TemplateMatcher
from modules.card_recognition.preproccess_data import ImagePreprocessor

class CardPipeline:
    def __init__(self):
        self.orb_recognizer = ORBCardRecognizer()
        self.template_matcher = TemplateMatcher()
        self.image_preprocessor = ImagePreprocessor()

    def recognize_card(self, image_path):
        """
        Recognize the card in the given image.

        Args:
            image_path (str): Path to the input image.

        Returns:
            dict: Detected card with rank and suit.
        """
        # Preprocess the image
        thresh_frame = self.image_preprocessor.preprocess_image(image_path)
        if thresh_frame is None:
            print("[DEBUG] Preprocessing failed.")
            return {"rank": None, "suit": None}

        # Step 1: Use ORB for recognition
        orb_result = self.orb_recognizer.detect_cards(thresh_frame)
        if orb_result:
            print(f"[DEBUG] ORB Recognition Result: {orb_result[0]}")
            return orb_result[0]

        # Step 2: Use Template Matching as a fallback
        print("[DEBUG] ORB failed. Using Template Matching.")
        detected_cards = self.template_matcher.detect_cards(image_path)
        if detected_cards:
            print(f"[DEBUG] Template Matching Result: {detected_cards[0]}")
            return detected_cards[0]

        # If both fail, return None
        print("[DEBUG] Both ORB and Template Matching failed.")
        return {"rank": None, "suit": None}
