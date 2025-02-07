import eventlet
eventlet.monkey_patch()

from flask import Flask, redirect, url_for, session, request, jsonify, render_template
from flask_socketio import SocketIO, emit, join_room, leave_room
from authlib.integrations.flask_client import OAuth
from config import Config
from pymongo import MongoClient
import datetime

from routes.users import users_bp, add_user
from routes.games import games_bp
from routes.reviews import reviews_bp

from utils.igdb_api import getTopGames, searchGame

# App setup
app = Flask(__name__)
app.config.from_object(Config)
socketio = SocketIO(app, cors_allowed_origins="*")
oauth = OAuth(app)

# Google OAuth setup using Authlib
google = oauth.register(
    name='google',
    client_id=app.config['GOOGLE_CLIENT_ID'],
    client_secret=app.config['GOOGLE_CLIENT_SECRET'],
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid profile email"}
)

mongoClient = MongoClient(app.config['MONGO_URI'])
database = mongoClient['GameAppDB']
usersCol = database["Users"]

with app.app_context():
    app.db = database

app.register_blueprint(users_bp, url_prefix='/users')
app.register_blueprint(games_bp, url_prefix='/games')
app.register_blueprint(reviews_bp, url_prefix='/reviews')


# ------------------------ Socket Handling ------------------------

@socketio.on("connect")
def handle_connect():
    if "user" in session:
        username = session["user"]["username"]
        socket_id = request.sid  # Unique socket ID

        usersCol.update_one({"username": username}, {
                            "$set": {"online": True}})

        print(f"{username} connected with socket ID {socket_id}")

        emit("user_status", {"username": username,
             "online": True}, broadcast=True)


@socketio.on("disconnect")
def handle_disconnect():
    if "user" in session:
        username = session["user"]["username"]

        usersCol.update_one({"username": username}, {
                            "$set": {"online": False}})

        print(f"{username} disconnected")

        emit("user_status", {"username": username,
             "online": False}, broadcast=True)

# ------------------------ Actual App Routes ------------------------


@app.route('/')
def home():
    # if user logged in, go to user's profile
    if 'user' in session:
        return redirect(url_for('users.user_profile'))

    # FIX USER IS NOT LOGGED IN AFTER REGISTERING

    return render_template("index.html")


@app.route('/home')
def homePage():

    if 'user' not in session:
        return render_template("index.html")

    # get the users profile from the session to check the lists they have
    wishlist = session['user'].get('profile', {}).get('wishlist', [])

    top_games = getTopGames(10)  # Get top 10 games
    return render_template("home.html", games=top_games, wishlist=wishlist)


@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    category = request.args.get('category')

    if category == 'users':
        # Search in users collection
        user = usersCol.find_one(
            {"username": {"$regex": query, "$options": "i"}})

        if user:
            return redirect(url_for('users.get_user', username=user['username']))
        return render_template('search_results.html', results="", category='users', gName=query)

    elif category == 'games':
        # Search in games collection

        foundGames = searchGame(query)
        wishlist = session['user'].get('profile', {}).get('wishlist', [])

        return render_template('search_results.html', games=foundGames, category='games', wishlist=wishlist, gName=query)

    else:
        return redirect(url_for('homePage'))


@app.route('/login')
def login():
    # redirect to Google's login page
    try:
        redirUri = url_for('authorized', _external=True)
        # generate state and save it in the session
        print(redirUri)
        return google.authorize_redirect(redirUri)
    except Exception as e:
        app.logger.error(f"Error during login {str(e)}")
        return "Error occured during login", 500


@app.route('/login/callback')
def authorized():
    token = google.authorize_access_token()
    userinfo_endpoint = google.server_metadata['userinfo_endpoint']
    resp = google.get(userinfo_endpoint)
    user_info_json = resp.json()

    print(user_info_json)
    # Check if user exists in DB
    user = usersCol.find_one({"email": user_info_json['email']})

    email = user_info_json['email']
    # default username, can be changed
    username = email.split('@')[0]

    if not user:
        profile = add_user(username, email)
    else:
        # get user's username and wishlist items
        username = user['username']
        profile = user['profile']

    # store info in session
    session['user'] = {
        'username': username,
        'email': email,
        'profile': profile
    }

    # if user exists -> profile page
    return redirect(url_for('users.user_profile'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


# ------------------------ Socket Handling ------------------------

@socketio.on("connect")
def handle_connect():
    if "user" in session:
        username = session["user"]["username"]
        socket_id = request.sid  # Unique socket ID

        usersCol.update_one({"username": username}, {
                            "$set": {"online": True}})

        print(f"{username} connected with socket ID {socket_id}")

        emit("user_status", {"username": username,
             "online": True}, broadcast=True)


@socketio.on("disconnect")
def handle_disconnect():
    if "user" in session:
        username = session["user"]["username"]

        usersCol.update_one({"username": username}, {
                            "$set": {"online": False}})

        print(f"{username} disconnected")

        emit("user_status", {"username": username,
             "online": False}, broadcast=True)


if __name__ == '__main__':
    app.run(debug=False)
