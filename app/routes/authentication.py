from flask import Blueprint, redirect, url_for, session, jsonify, request
from authlib.integrations.flask_client import OAuth
from config import Config
import bcrypt
from database import Database_Manager
import traceback

auth_bp = Blueprint('auth_bp', __name__)
oauth = OAuth()
db_manager = Database_Manager()

def config_oauth(app):
    oauth.init_app(app)
    oauth.register(
        'auth0',
        client_id=Config.AUTH0_CLIENT_ID,
        client_secret=Config.AUTH0_CLIENT_SECRET,
        api_base_url=Config.AUTH0_DOMAIN,
        access_token_url=Config.AUTH0_ACCESS_TOKEN,
        authorize_url=Config.AUTH0_AUTH,
        client_kwargs={'scope': 'openid profile email'},
    )

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    user_name = data.get('user_name')
    password = data.get('password')

    if not user_name or not password:
        return jsonify({"error": "Missing username or password"}), 400

    try:
        user = db_manager.get_user_by_username(user_name)
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            session['user_id'] = user['user_id']
            return jsonify({"message": "Login successful", "user_id": user['user_id']}), 200
        else:
            return jsonify({"error": "Invalid username or password"}), 401
    except Exception as e:
        print("Failed to login user:", e)
        traceback.print_exc()
        return jsonify({"error": "Unable to login user"}), 500

@auth_bp.route('/callback')
def callback():
    token = oauth.auth0.authorize_access_token()
    resp = oauth.auth0.get('userinfo')
    userinfo = resp.json()
    session['user'] = userinfo
    return redirect('/conversation')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth_bp.login'))

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.json
    user_name = data.get('user_name')
    password = data.get('password')

    if not user_name or not password:
        return jsonify({"error": "Missing username or password"}), 400

    # Hash the password before storing it
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    try:
        user_id = db_manager.insert_user(user_name, hashed_password.decode('utf-8'))  # Ensure the hashed password is stored as a string
        return jsonify({"message": "User created successfully", "user_id": user_id}), 201
    except Exception as e:
        print("Failed to insert user:", e)
        traceback.print_exc()  # Print the full stack trace
        return jsonify({"error": "Unable to create user"}), 500