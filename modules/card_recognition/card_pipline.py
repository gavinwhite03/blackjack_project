from .ORB import detect_card
from .template_matching import TemplateMatcher

def recognize_card(image):
    """
    Recognize the card in the given image.

    Args:
        image (numpy.ndarray): Input image.

    Returns:
        dict: Detected card with rank and suit.
    """
    # Initialize TemplateMatcher
    matcher = TemplateMatcher()

    # Detect the card using ORB
    orb_result = detect_card(image)

    # If ORB fails, use template matching as a fallback
    if orb_result["rank"] is None or orb_result["suit"] is None:
        templates_result = matcher.detect_cards(image)
        if templates_result:
            return templates_result[0]  # Return the first detected card

    return orb_result