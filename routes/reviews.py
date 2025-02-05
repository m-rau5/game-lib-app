from flask import Blueprint, request, jsonify, current_app
from datetime import datetime

reviews_bp = Blueprint('reviews', __name__)
db = None

# Add a review for a game


@reviews_bp.before_app_request
def init_db():
    global db
    db = db = current_app.db
    global users_collection
    users_collection = db['Users']
    global reviews_collection
    reviews_collection = db["Reviews"]


@reviews_bp.route('/add', methods=['POST'])
def add_review():
    data = request.get_json()
    username = data.get('username')
    game_id = data.get('game_id')
    rating = data.get('rating')
    review_text = data.get('review', '')

    if not username or not game_id or rating is None:
        return jsonify({"error": "Username, game ID, and rating are required"}), 400

    user = users_collection.find_one({"username": username})
    if not user:
        return jsonify({"error": "User not found"}), 404

    review = {
        "username": user['username'],
        "game_id": game_id,
        "rating": rating,
        "review": review_text,
        "created_at": datetime.utcnow()
    }

    reviews_collection.insert_one(review)
    return jsonify({"message": "Review added successfully!"}), 201


# Get all reviews for a game
@reviews_bp.route('/<game_id>', methods=['GET'])
def get_reviews(game_id):
    reviews = list(reviews_collection.find({"game_id": game_id}, {"_id": 0}))
    if not reviews:
        return jsonify({"message": "No reviews for this game yet."}), 200
    return jsonify(reviews), 200
