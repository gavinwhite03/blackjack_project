from flask import Flask, jsonify, render_template
from modules.cloud_integration import fetch_card_count, fetch_game_stats, init_firebase, fetch_player1_data

app = Flask(__name__)

init_firebase()

@app.route('/')
def home():
    """
    Serve the main dashboard page.
    """
    return render_template('dashboard.html')  # This serves the HTML file

@app.route('/card_count', methods=['GET'])
def get_card_count():
    """
    Fetch the current card count and optimal action from Firebase.
    """
    card_count_data = fetch_card_count()
    return jsonify(card_count_data)

@app.route('/game_stats', methods=['GET'])
def get_game_stats():
    """
    Fetch the game stats (e.g., total games, wins, losses) from Firebase.
    """
    game_stats = fetch_game_stats()
    return jsonify(game_stats)

@app.route('/player1', methods=['GET'])
def get_player1_data():
    """
    Fetch Player1's detected cards and optimal action from Firebase.
    """
    player1_data = fetch_player1_data
    return jsonify(player1_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)