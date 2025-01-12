import cv2
import os
import numpy as np

class ImagePreprocessor:
    def __init__(self, input_dir=None, output_dir=None, size=(128, 128), threshold=120):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.size = size
        self.threshold = threshold

        # Ensure the output directory exists
        if self.output_dir and not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def preprocess_image(self, img_or_path, category=None, filename=None):
        """
        Preprocess an image for card recognition.

        Args:
            img_or_path (str or numpy.ndarray): Path to the image or the image itself.
            category (str): Category of the card (optional, for saving/debugging).
            filename (str): Filename of the image (optional, for saving/debugging).

        Returns:
            tuple: Grayscale frame and thresholded frame.
        """
        # If input is a path, load the image
        if isinstance(img_or_path, (str, os.PathLike)):
            if not os.path.exists(img_or_path):
                # print(f"[ERROR] Invalid image path: {img_or_path}")
                return None, None
            img = cv2.imread(img_or_path)
        elif isinstance(img_or_path, np.ndarray):
            img = img_or_path
        else:
            print(f"[ERROR] Invalid input type: {type(img_or_path)}")
            return None, None

        # Convert to grayscale
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Apply Blur
        blurred_img = cv2.GaussianBlur(gray_img, (5, 5), 0)

        # Resize image to the specified size
        resized_img = blurred_img

        # Apply thresholding
        _, threshold_img = cv2.threshold(resized_img, self.threshold, 255, cv2.THRESH_BINARY)

        # Save the processed image if output_dir is provided
        if self.output_dir and category and filename:
            filename_finished = f"{category}_{filename}"
            output_path = os.path.join(self.output_dir, filename_finished)
            cv2.imwrite(output_path, threshold_img)
            print(f"Processed and saved: {output_path}")

        return threshold_img

    def preprocess_directory(self, category):
        """Preprocess all images in the input directory."""
        for filename in os.listdir(self.input_dir):
            if filename.endswith('.jpg'):
                img_path = os.path.join(self.input_dir, filename)
                self.preprocess_image(img_path, category, filename)

# Main execution
if __name__ == "__main__":
    input_dir = '/home/gman/blackjack_project/tests/test_dataset'
    output_dir = '/home/gman/blackjack_project/processed_dataset/thresholded/cropped/suit'

    # Initialize the preprocessor
    preprocessor = ImagePreprocessor(input_dir, output_dir)

    # Preprocess all images with category "suit"
    preprocessor.preprocess_directory(category="suit")
