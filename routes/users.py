from flask import Blueprint, request, jsonify, current_app, render_template, redirect, url_for, session
from datetime import datetime
import time

users_bp = Blueprint('users', __name__)
db = None

# Create a new user


@users_bp.before_app_request
def init_db():
    global db
    db = current_app.db
    global usersCol
    usersCol = db['Users']


def add_user(username, email):
    if not username or not email:
        return False
        # return jsonify({"error": "Username and email are required"}), 400

    if usersCol.find_one({"email": email}):
        return False
        # return jsonify({"message": "User with this email already exists"}), 400

    if usersCol.find_one({"username": username}):
        return False
        # return jsonify({"message": "Username already taken."}), 400

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
    return user.get("profile")


# Get user profile by username
@users_bp.route('/<username>', methods=['GET'])
def get_user(username):
    user = usersCol.find_one({"username": username}, {
        "_id": 0})
    if not user:
        return jsonify({"error": "User not found"}), 404
    return render_template('user_preview.html', user=user)


@users_bp.route('/user_profile', methods=['GET'])
def user_profile():
    if 'user' not in session:
        return redirect(url_for('home'))  # Redirect if not authorized

    username = session['user']['username']
    user = usersCol.find_one({"username": username})

    # restrict access to only the logged-in user's profile
    if session['user']['username'] != username:
        return redirect(url_for('home'))

    if user:
        return render_template('user_profile.html', user=user)
    else:
        return redirect(url_for('home'))


@users_bp.route("/user_profile/change_username", methods=["POST"])
def change_username():
    if "user" not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401

    data = request.json
    newUsername = data.get("new_username")
    currentUser = session["user"]["username"]

    # empty username
    if not newUsername:
        return jsonify({"success": False, "message": "Username cannot be empty"}), 400

    # username exists
    if usersCol.find_one({"username": newUsername}):
        return jsonify({"success": False, "message": "Username already taken"}), 400

    # updating the username
    usersCol.update_one({"username": currentUser}, {
                        "$set": {"username": newUsername}})

    session["user"]["username"] = newUsername
    session.modified = True  # force-recognize the session change

    return jsonify({"success": True, "message": "Username updated successfully"})


@users_bp.route("/update_wishlist", methods=["POST"])
def update_wishlist():
    if "user" not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401

    data = request.json
    # make string preemptively since thats how we store it
    gameId = str(data.get("game_id"))

    if not gameId:
        return jsonify({"success": False, "message": "Invalid game ID"}), 400

    username = session["user"]["username"]

    # get user profile
    user = usersCol.find_one({"username": username})
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    # check in wishlist AND in session's wishlist
    wishlist = user["profile"].get("wishlist", [])
    sessionWishlist = session['user'].get('profile', {}).get('wishlist', [])
    # print(sessionWishlist)

    if gameId in wishlist:
        # remove from wishlist
        usersCol.update_one(
            {"username": username},
            {"$pull": {"profile.wishlist": gameId}}
        )
        if gameId in sessionWishlist:
            sessionWishlist.remove(gameId)
            session.modified = True
        return jsonify({"success": True, "message": "Game removed from wishlist", "in_wishlist": False})
    else:
        # add to wishlist
        usersCol.update_one(
            {"username": username},
            {"$push": {"profile.wishlist": gameId}}
        )
        if gameId not in sessionWishlist:
            sessionWishlist.append(gameId)
            session.modified = True
        return jsonify({"success": True, "message": "Game added to wishlist", "in_wishlist": True})
