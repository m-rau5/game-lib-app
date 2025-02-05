from flask import Blueprint, request, jsonify, current_app
from datetime import datetime

games_bp = Blueprint('games', __name__)


# initialize db connetion and collections
@games_bp.before_app_request
def init_db():
    global db
    db = current_app.db
    global users_collection
    users_collection = db['Users']


# Add a game to a user's profile
@games_bp.route('/<username>/add', methods=['POST'])
def add_game(username):
    data = request.get_json()
    game_id = data.get('game_id')
    status = data.get('status')

    if status not in ['currently_playing', 'finished', 'dropped', 'wishlist']:
        return jsonify({"error": "Invalid status."}), 400

    user = users_collection.find_one({"username": username})
    if not user:
        return jsonify({"error": "User not found"}), 404

    users_collection.update_one(
        {"username": username},
        {"$push": {f"profile.{status}": {"game_id": game_id, "added_at": datetime.utcnow()}}}
    )

    return jsonify({"message": f"Game {game_id} added to {status} list."}), 200