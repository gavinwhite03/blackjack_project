import cv2
from multiprocessing import Process
from modules.card_detection import DetectCards
from modules.blackjack_strategy import calculate_optimal_action, update_card_count, check_game_result
from modules.cloud_integration import init_firebase, update_player_cards, update_data, log_game_result
from modules.web_server import app



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
        player1_roi = frame[height // 2:, :]  # Bottom left

        # Wait for 'p' key to process cards
        key = cv2.waitKey(1) & 0xFF
        if key == ord('p'):
            # Detect cards for Player1
            player_roi_name, player_cards = DetectCards.detect_in_roi("Player1", player1_roi)
            print(f"{player_roi_name}: {player_cards}")

            # Detect cards for Dealer
            dealer_roi_name, dealer_cards = DetectCards.detect_in_roi("Dealer", dealer_roi)
            print(f"{dealer_roi_name}: {dealer_cards}")

            # Update card count
            card_count = update_card_count(card_count, player_cards + dealer_cards)
            print(f"Updated Card Count: {card_count}")

            # Calculate optimal action for Player based on Dealer's visible card and card count
            optimal_action = calculate_optimal_action(player_cards, dealer_cards[0] if dealer_cards else None, card_count)
            print(optimal_action)

            # Update Firebase
            update_player_cards(player_roi_name, player_cards, optimal_action)
            update_player_cards(dealer_roi_name, dealer_cards, "N/A")
            update_data('/CardCount', card_count)
            update_data('/GameState/Player1/optimal_action', optimal_action)
            
            if len(dealer_cards) >= 2:
                # Check game result
                result = check_game_result(player_cards, dealer_cards)
                log_game_result(result)
                print(f"Game Result: {result}")
            

        # Display ROIs for visual feedback
        cv2.imshow('Dealer ROI', dealer_roi)
        cv2.imshow('Player1 ROI', player1_roi)

        # Exit on 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()

def run_flask():
    app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    # Start Flask server and card detection concurrently
    flask_process = Process(target=run_flask)
    flask_process.start()

    try:
        # Run card detection logic
        main()
    except KeyboardInterrupt:
        print("Shutting down...")

    # Ensure Flask server stops
    flask_process.terminate()
    flask_process.join()
