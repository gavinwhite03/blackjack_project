import cv2
import os

class ImagePreprocessor:
    def __init__(self, input_dir, output_dir, size=(128, 128), threshold=120):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.size = size
        self.threshold = threshold

        # Ensure the output directory exists
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def preprocess_image(self, img_path, category, filename):
        """Preprocess a single image."""
        # Read the image
        img = cv2.imread(img_path)
        if img is None:
            print(f"Failed to load image: {img_path}")
            return

        # Convert to grayscale
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Resize image to the specified size
        resized_img = cv2.resize(gray_img, self.size)

        # Apply thresholding
        _, threshold_img = cv2.threshold(resized_img, self.threshold, 255, cv2.THRESH_BINARY)

        # Save the processed image
        filename_finished = f"{category}_{filename}"
        output_path = os.path.join(self.output_dir, filename_finished)
        cv2.imwrite(output_path, threshold_img)

        print(f"Processed and saved: {output_path}")

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
