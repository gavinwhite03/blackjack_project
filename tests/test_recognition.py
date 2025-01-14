import cv2
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from modules.card_recognition.card_pipline import recognize_card

# Test dataset path
test_dataset = "/home/gman/blackjack_project/tests/test_dataset"
templates_dir = "/home/gman/blackjack_project/templates"

# Test the recognition system
for filename in os.listdir(test_dataset):
    if filename.endswith('.jpg'):
        file_path = os.path.join(test_dataset, filename)
        test_image = cv2.imread(file_path, 0)

        # Recognize the card
        result = recognize_card(test_image, templates_dir)
        rank = result.get("rank", "Unkown")
        suit = result.get("suit", "Unknown")
        
        print(f"Test Image: {filename}, Detected Rank: {rank}, Detected Suit: {suit}")