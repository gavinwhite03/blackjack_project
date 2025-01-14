import cv2
from modules.card_detection import DetectCards
from modules.blackjack_strategy import calculate_optimal_action
from modules.cloud_integration import init_firebase, update_player_cards

# Initialize Firebase
init_firebase()

def main():
    print("Starting Blackjack AI Assistant...")

    # Initialize webcam
    cap = cv2.VideoCapture(0)

    # Game state
    card_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture image.")
            break

        # Get frame dimensions
        height, width, _ = frame.shape

        # Define ROIs
        dealer_roi = frame[:height // 2, :]  # Top half
        player1_roi = frame[height // 2:, :width // 2]  # Bottom left
        player2_roi = frame[height // 2:, width // 2:]  # Bottom right

        rois = [
            ("Dealer", dealer_roi),
            ("Player1", player1_roi),
            ("Player2", player2_roi)
        ]

        # Wait for 'p' key to process cards
        key = cv2.waitKey(1) & 0xFF
        if key == ord('p'):
            for name, roi in rois:
                # Detect cards for each ROI
                detected_cards = DetectCards(roi)

                # Calculate optimal action for Player hands (skip for Dealer)
                if name != "Dealer":
                    dealer_card = DetectCards(dealer_roi)
                    optimal_action = calculate_optimal_action(detected_cards, dealer_card[0] if dealer_card else None, card_count)
                else:
                    optimal_action = "N/A"

                # Update card count (simplified example using +1 for each card detected)
                card_count += len(detected_cards)

                # Update Firebase
                update_player_cards(name, detected_cards, optimal_action)

                # Print results
                print(f"{name}: Cards = {detected_cards}, Action = {optimal_action}")

        # Display ROIs for visual feedback
        cv2.imshow('Dealer ROI', dealer_roi)
        cv2.imshow('Player1 ROI', player1_roi)
        cv2.imshow('Player2 ROI', player2_roi)

        # Exit on 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
