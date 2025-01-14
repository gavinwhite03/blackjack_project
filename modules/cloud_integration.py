import firebase_admin
from firebase_admin import credentials, db

# Initialize Firebase
def init_firebase():
    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://blackjack-agent-default-rtdb.europe-west1.firebasedatabase.app/'
    })

# Update data in Firebase
def update_data(path, data):
    ref = db.reference(path)
    ref.set(data)

# Fetch data from Firebase
def fetch_data(path):
    ref = db.reference(path)
    return ref.get()

def initialize_data():
    ref = db.reference('/')
    ref.set({
                {
        "GameState": {
            "Dealer": {
            "cards": ["Ace", "King"],
            "optimal_action": "Stand"
            },
            "Player1": {
            "cards": ["7", "9"],
            "optimal_action": "Hit"
            },
            "Player2": {
            "cards": ["5", "6"],
            "optimal_action": "Hit"
            }
        },
        "GameStats": {
            "total_games": 10,
            "wins": 6,
            "losses": 4
            }
        }
    })

def update_card_count(count, action):
    ref = db.reference('/CardCount')
    ref.update({
        "count": count,
        "optimal_action": action
    })

def log_game_result(result):
    ref = db.reference('/GameStats')
    stats = ref.get() or {"total_games": 0, "wins": 0, "losses": 0}
    
    stats["total_games"] += 1
    if result == "win":
        stats["wins"] += 1
    elif result == "loss":
        stats["losses"] += 1

    ref.set(stats)

def fetch_card_count():
    ref = db.reference('/CardCount')
    return ref.get()

def fetch_game_stats():
    ref = db.reference('/GameStats')
    return ref.get()

def update_player_cards(player, cards, action):
    """
    Update the cards and optimal action for a specific player or dealer in Firebase.
    :param player: String ('Dealer', 'Player1', 'Player2').
    :param cards: List of card ranks.
    :param action: String, optimal action (e.g., 'Hit', 'Stand').
    """
    ref = db.reference(f'/GameState/{player}')
    ref.set({
        "cards": cards,
        "optimal_action": action
    })

def fetch_player_cards(player):
    """
    Fetch the cards and optimal action for a specific player or dealer.
    :param player: String ('Dealer', 'Player1', 'Player2').
    :return: Dictionary with cards and optimal action.
    """
    ref = db.reference(f'/GameState/{player}')
    return ref.get()

def update_player_cards(player, cards, action):
    """
    Update the cards and optimal action for a specific player or dealer in Firebase.
    :param player: String ('Dealer', 'Player1', 'Player2').
    :param cards: List of card ranks.
    :param action: String, optimal action (e.g., 'Hit', 'Stand').
    """
    ref = db.reference(f'/GameState/{player}')
    ref.set({
        "cards": cards,
        "optimal_action": action
    })


if __name__ == "__main__":
    # Example usage
    init_firebase()
    update_data('/CardCount', {'count': 0, 'optimal_action': 'N/A'})
    print(fetch_data('/CardCount'))
