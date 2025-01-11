from modules.card_recognition.ORB import ORBCardRecognizer
from modules.card_recognition.template_matching import TemplateMatcher
from modules.card_recognition.preproccess_data import ImagePreprocessor

# Initialize 
orb_recognizer = ORBCardRecognizer()
template_matcher = TemplateMatcher()
image_preprocessor = ImagePreprocessor()


def recognize_card(image_path):
    """
    Recognize the card in the given image.

    Args:
        image_path (str): Path to the input image.

    Returns:
        dict: Detected card with rank and suit.
    """
    # print(f"[DEBUG] Image Path: {image_path}")
    # Call preprocess_image and pass the image path
    gray_frame, thresh_frame = image_preprocessor.preprocess_image(image_path)

    # Handle cases where preprocessing fails
    if gray_frame is None or thresh_frame is None:
        print("[DEBUG] Preprocessing failed.")
        return {"rank": None, "suit": None}

    # Step 1: Use ORB for recognition
    orb_result = orb_recognizer.detect_cards(gray_frame, thresh_frame)
    if orb_result and len(orb_result) > 0:
        print(f"[DEBUG] ORB Recognition Result: {orb_result[0]}")
        return orb_result[0]

    # Step 2: Use Template Matching as a fallback
    print("[DEBUG] ORB failed. Using Template Matching.")
    detected_cards = template_matcher.detect_cards(image_path)
    if detected_cards:
        print(f"[DEBUG] Template Matching Result: {detected_cards[0]}")
        return detected_cards[0]

    # If both fail, return None
    print("[DEBUG] Both ORB and Template Matching failed.")
    return {"rank": None, "suit": None}