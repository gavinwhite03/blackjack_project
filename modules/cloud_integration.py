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
        "CardCount": {
            "count": 0,
            "optimal_action": "N/A"
        },
        "GameStats": {
            "total_games": 0,
            "wins": 0,
            "losses": 0
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


if __name__ == "__main__":
    # Example usage
    init_firebase()
    update_data('/CardCount', {'count': 0, 'optimal_action': 'N/A'})
    print(fetch_data('/CardCount'))
