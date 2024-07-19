from flask import Blueprint, redirect, url_for, session, jsonify, request, render_template_string
from authlib.integrations.flask_client import OAuth
from config import Config
import bcrypt
import pyotp
import qrcode
import io
import base64
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

html_template = """
<!doctype html>
<html lang="en">
  <head>
    <title>Google Authenticator</title>
  </head>
  <body>
    <h1>Scan this QR code with Google Authenticator</h1>
    <img src="data:image/png;base64, {{ qr_code }}">
  </body>
</html>
"""

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.json
    user_name = data.get('user_name')
    password = data.get('password')

    if not user_name or not password:
        return jsonify({"error": "Missing username or password"}), 400

    # Hash the password before storing it
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    try:
        # Generate TOTP secret
        totp_secret = pyotp.random_base32()

        # Insert user with TOTP secret
        user_id = db_manager.insert_user(user_name, hashed_password, totp_secret)
        
        return jsonify({"message": "User created successfully!", "user_id": user_id, "totp_secret": totp_secret}), 201
    except Exception as e:
        print("Failed to insert user:", e)
        traceback.print_exc()
        return jsonify({"error": "Unable to create user", "details": str(e)}), 500

@auth_bp.route('/qrcode/<user_id>/<totp_secret>', methods=['GET'])
def qrcode_route(user_id, totp_secret):
    try:
        user = db_manager.get_user_by_id(user_id)
        if user:
            totp = pyotp.TOTP(totp_secret)
            otpauth_url = totp.provisioning_uri(name=user['user_name'], issuer_name="Secure LLM Api")

            qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
            qr.add_data(otpauth_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            qr_code_base64 = base64.b64encode(buffered.getvalue()).decode()

            # Return the HTML page with the embedded QR code
            return render_template_string(html_template, qr_code=qr_code_base64)
        else:
            return jsonify({"error": "User not found"}), 404
    except Exception as e:
        print("Error generating QR code:", e)
        traceback.print_exc()
        return jsonify({"error": "Unable to generate QR code", "details": str(e)}), 500

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
            return jsonify({"message": "Password verified, please provide the TOTP token"}), 200
        else:
            return jsonify({"error": "Invalid username or password"}), 401
    except Exception as e:
        print("Failed to login user:", e)
        traceback.print_exc()
        return jsonify({"error": "Unable to login user"}), 500

@auth_bp.route('/verify-token', methods=['POST'])
def verify_token():
    data = request.json
    user_id = data['user_id']
    token = data['token']

    try:
        totp_secret = db_manager.get_totp_secret(user_id)
        if totp_secret:
            totp = pyotp.TOTP(totp_secret)
            if totp.verify(token):
                return jsonify({"verified": True}), 200
            else:
                return jsonify({"verified": False}), 401
        else:
            return jsonify({"error": "TOTP secret not found"}), 404
    except Exception as e:
        print("Failed to verify token:", e)
        traceback.print_exc()
        return jsonify({"error": "Unable to verify token"}), 500

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

@auth_bp.route('/generate-qrcode/<username>', methods=['GET'])
def generate_qrcode(username):
    user = db_manager.get_user_by_username(username)
    if user:
        totp_secret = pyotp.random_base32()
        db_manager.set_totp_secret(user["user_id"], totp_secret)

        totp = pyotp.TOTP(totp_secret)
        otpauth_url = totp.provisioning_uri(name=username, issuer_name="YourApp")

        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(otpauth_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        qr_code_base64 = base64.b64encode(buffered.getvalue()).decode()

        return render_template_string(html_template, qr_code=qr_code_base64)
    else:
        return jsonify({"error": "User not found"}), 404

@auth_bp.route('/protected-route', methods=['GET'])
def protected_route():
    username = request.headers.get('username')
    token = request.headers.get('token')

    if not username or not token:
        return jsonify({"error": "Missing credentials"}), 403

    user = db_manager.get_user_by_username(username)
    if user:
        totp_secret = user['totp_secret']
        totp = pyotp.TOTP(totp_secret)

        if totp.verify(token):
            return jsonify({"message": "You have access to this route!"})
        else:
            return jsonify({"error": "Invalid token"}), 403
    else:
        return jsonify({"error": "User not found"}), 403
