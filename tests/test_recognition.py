import cv2
import os
import logging
from modules.card_recognition.card_pipeline import recognize_card

# Configure logging
logging.basicConfig(filename="test_results.log", level=logging.INFO, format="%(asctime)s - %(message)s")

def load_test_images(test_dir):
    """
    Load test images from the given directory.

    Args:
        test_dir (str): Path to the directory containing test images.

    Returns:
        list: A list of tuples (filename, image).
    """
    test_images = []
    for filename in os.listdir(test_dir):
        if filename.endswith('.jpg'):
            file_path = os.path.join(test_dir, filename)
            image = cv2.imread(file_path)
            if image is not None:
                test_images.append((filename, image))
            else:
                logging.warning(f"Failed to load image: {file_path}")
    return test_images

def test_card_recognition(test_images):
    """
    Test the card recognition system on a list of test images.

    Args:
        test_images (list): List of tuples (filename, image).

    Returns:
        list: A list of tuples (filename, expected_result, detected_result).
    """
    results = []
    for filename, image in test_images:
        # Extract the expected rank and suit from the filename
        try:
            expected_rank, expected_suit = filename.split('_of_')[0], filename.split('_of_')[1][:-4]
        except IndexError:
            logging.error(f"Invalid filename format: {filename}")
            continue

        # Run the recognition pipeline
        detected_result = recognize_card(image)
        detected_rank, detected_suit = detected_result.get("rank"), detected_result.get("suit")

        # Log the result
        log_message = f"Test Image: {filename}, Expected: {expected_rank} of {expected_suit}, Detected: {detected_rank} of {detected_suit}"
        logging.info(log_message)
        print(log_message)

        # Append to results
        results.append((filename, f"{expected_rank} of {expected_suit}", f"{detected_rank} of {detected_suit}"))

    return results

def evaluate_results(results):
    """
    Evaluate the results of the card recognition test.

    Args:
        results (list): A list of tuples (filename, expected_result, detected_result).

    Returns:
        None
    """
    correct = 0
    total = len(results)

    for filename, expected_result, detected_result in results:
        if expected_result.lower() == detected_result.lower():
            correct += 1
        else:
            print(f"Mismatch: {filename} -> Expected: {expected_result}, Detected: {detected_result}")
            logging.warning(f"Mismatch: {filename} -> Expected: {expected_result}, Detected: {detected_result}")

    accuracy = (correct / total) * 100 if total > 0 else 0
    print(f"Total Images: {total}, Correctly Detected: {correct}, Accuracy: {accuracy:.2f}%")
    logging.info(f"Total Images: {total}, Correctly Detected: {correct}, Accuracy: {accuracy:.2f}%")

# Main testing function
if __name__ == "__main__":
    # Path to the test dataset
    test_dir = "test_dataset"  # Replace with your test dataset path

    # Load test images
    test_images = load_test_images(test_dir)
    if not test_images:
        print("No test images found. Check the test dataset directory.")
        logging.error("No test images found in the test directory.")
        exit()

    # Test the card recognition system
    results = test_card_recognition(test_images)

    # Evaluate the results
    evaluate_results(results)
