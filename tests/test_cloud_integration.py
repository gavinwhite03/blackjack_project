import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.cloud_integration import (
    init_firebase,
    initialize_data,
    update_card_count,
    fetch_card_count,
    log_game_result,
    fetch_game_stats
)

def run_tests():
    print("Initializing Firebase...")
    init_firebase()

    print("Setting initial data structure...")
    initialize_data()

    print("Testing card count update...")
    update_card_count(3, "Hit")
    card_data = fetch_card_count()
    print(f"Card Count: {card_data['count']}, Optimal Action: {card_data['optimal_action']}")

    print("Testing game stats logging...")
    log_game_result("win")
    log_game_result("loss")
    stats = fetch_game_stats()
    print(f"Game Stats: {stats}")

if __name__ == "__main__":
    run_tests()
