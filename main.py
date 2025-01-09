import cv2
import firebase_admin
from firebase_admin import credentials, db
from modules.cloud_integration import init_firebase, initialize_data, update_card_count, log_game_result, fetch_card_count, fetch_game_stats


print("Libraries imported successfully!")

def main():
    init_firebase()
    initialize_data()
    print("Starting Blackjack AI Assistant...")

if __name__ == "__main__":
    main()

detected_count = 5
optimal_action = "Hit"
update_card_count(detected_count, optimal_action)

log_game_result("win")

card_count = fetch_card_count()
print(f"Current Card Count: {card_count['count']}, Optimal Action: {card_count['optimal_action']}")

game_stats = fetch_game_stats()
print(f"Total Games: {game_stats['total_games']}, Wins: {game_stats['wins']}, Losses: {game_stats['losses']}")
