from flask import Blueprint, request, jsonify, current_app, render_template, redirect, url_for, session
from datetime import datetime

users_bp = Blueprint('users', __name__)
db = None

# Create a new user


@users_bp.before_app_request
def init_db():
    global db
    db = current_app.db
    global usersCol
    usersCol = db['Users']


@users_bp.route('/add', methods=['POST'])
def add_user():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')   # emails are unique since we login usig google

    if not username or not email:
        return jsonify({"error": "Username and email are required"}), 400

    if usersCol.find_one({"email": email}):
        return jsonify({"message": "User with this email already exists"}), 400

    if usersCol.find_one({"username": username}):
        return jsonify({"message": "Username already taken."}), 400

    user = {
        "username": username,
        "email": email,
        "online": False,
        "profile": {
            "currently_playing": [],
            "finished": [],
            "dropped": [],
            "wishlist": []
        },
        "created_at": datetime.utcnow()
    }

    usersCol.insert_one(user)
    return jsonify({"message": f"User {username} added successfully!"}), 201


# Get user profile by username
@users_bp.route('/<username>', methods=['GET'])
def get_user(username):
    user = usersCol.find_one({"username": username}, {
        "_id": 0})
    if not user:
        return jsonify({"error": "User not found"}), 404
    return render_template('user_preview.html', user=user)


@users_bp.route('/user_profile/', methods=['GET'])
def user_profile(username=None):
    if 'user' not in session:
        return redirect(url_for('home'))  # Redirect if not authorized

    # Default to logged-in user's username if none provided
    if username is None:
        username = session['user']['username']

    user = usersCol.find_one({"username": username})

    # Restrict access to only the logged-in user's profile
    if session['user']['username'] != username:
        return redirect(url_for('home'))

    if user:
        return render_template('user_profile.html', user=user)
    else:
        return redirect(url_for('home'))
