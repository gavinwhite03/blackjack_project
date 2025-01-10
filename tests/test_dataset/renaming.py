import os

def rename_images(directory):
    """
    Rename all images in the given directory to follow the 'rank_suit.jpg' naming convention.

    Args:
        directory (str): Path to the directory containing images.
    """
    for filename in os.listdir(directory):
        if filename.endswith('.jpg'):
            # Split the filename into rank and suit based on ' of '
            try:
                rank, suit_with_extension = filename.split('_')
                suit = suit_with_extension.split('.')[0]  # Remove '.jpg'
                new_filename = f"{rank.lower()}_of_{suit.lower()}.jpg"

                # Construct full paths
                old_path = os.path.join(directory, filename)
                new_path = os.path.join(directory, new_filename)

                # Rename the file
                os.rename(old_path, new_path)
                print(f"Renamed: {filename} -> {new_filename}")
            except ValueError:
                print(f"Skipping file (invalid format): {filename}")

# Main execution
if __name__ == "__main__":
    directory = "/home/gman/blackjack_project/tests/test_dataset"  # Replace with the path to your image directory
    rename_images(directory)
