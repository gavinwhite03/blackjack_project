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
    """
    Log the game result (win/loss/tie) and update Firebase.
    :param result: String ('win', 'loss', or 'tie').
    """
    ref = db.reference('/GameStats')
    stats = ref.get() or {"total_games": 0, "wins": 0, "losses": 0}

    stats["total_games"] += 1
    if result == "win":
        stats["wins"] += 1
    elif result == "loss":
        stats["losses"] += 1

    ref.set(stats)
    print(f"Game result logged: {result}")


def fetch_card_count():
    ref = db.reference('/CardCount')
    card_count_data = ref.get()
    print(f"Card Count Data from API: {card_count_data}")  # Debugging output
    if card_count_data is None:
        return {"count": 0}  # Default values
    return card_count_data

def fetch_game_stats():
    ref = db.reference('/GameStats')
    game_stats = ref.get()
    print(f"Game Stats Data: {game_stats}")  # Debugging output
    if game_stats is None:
        return {"total_games": 0, "wins": 0, "losses": 0}  # Default values
    return game_stats

def update_player_cards(player, cards, action):
    """
    Update the cards and optimal action for a specific player or dealer in Firebase.
    :param player: String ('Dealer', 'Player1').
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
    :param player: String ('Dealer', 'Player1').
    :param cards: List of card ranks.
    :param action: String, optimal action (e.g., 'Hit', 'Stand').
    """
    ref = db.reference(f'/GameState/{player}')
    ref.set({
        "cards": cards,
        "optimal_action": action
    })

def fetch_player1_data():
    """
    Fetch Player1's detected cards and optimal action from Firebase.
    """
    ref = db.reference('/GameState/Player1')
    player1_data = ref.get()
    print(f"Fetched Player1 Data: {player1_data}")
    if player1_data is None:
        print("No data found for Player1 in Firebase.")
        return {"cards": [], "optimal_action": "N/A"}
    player1_data.setdefault("optimal_action", "N/A")
    return player1_data




if __name__ == "__main__":
    # Example usage
    init_firebase()
    update_data('/CardCount', {'count': 0})
    print(fetch_data('/CardCount'))
