from flask import Flask, redirect, url_for, session, request, jsonify, render_template
from authlib.integrations.flask_client import OAuth
from config import Config
from pymongo import MongoClient
import datetime

from routes.users import users_bp
from routes.games import games_bp
from routes.reviews import reviews_bp

# App setup
app = Flask(__name__)
app.config.from_object(Config)

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


@app.route('/')
def home():
    # if user logged in, go to user's profile
    if 'user' in session:
        return redirect(url_for('users.user_profile'))
    
    # FIX USER IS NOT LOGGED IN AFTER REGISTERING

    return render_template("index.html")


@app.route('/home')
def homePage():
    return render_template("home.html")


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
        return render_template('search_results.html', results="", category='Users')

    elif category == 'games':
        # Search in games collection

        # MAKE API_HELPER TO SEARCH GAME WITH THESE NAMES!!!

        results = ""

        return render_template('search_results.html', results=results, category='Games')

    else:
        return redirect(url_for('homePage'))


@app.route('/login')
def login():
    # Redirect to Google's login page
    try:
        redirUri = url_for('authorized', _external=True)
        redirUri = redirUri.replace('127.0.0.1', 'localhost')
        # Generate state and save it in the session
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
        # create new user if not existant
        new_user = {
            "username": username,
            "email": email,
            "created_at": datetime.datetime.now()
        }
        usersCol.insert_one(new_user)

        # profile page with temp_username
        return redirect(url_for('users.user_profile'))
    else:
        username = user['username']

    # store info in session
    session['user'] = {
        'username': username,
        'email': email
    }

    # if user exists -> profile page
    return redirect(url_for('users.user_profile'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
