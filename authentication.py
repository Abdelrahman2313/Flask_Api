# auth.py

from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import create_access_token
from database import mysql
import bcrypt
import pyotp
import qrcode
import io

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    password = data['password']
    
    
    twofa_secret = pyotp.random_base32()

    
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO users (username, password, twofa_secret) VALUES (%s, %s, %s)", 
                   (username, hashed_password.decode(), twofa_secret))
    mysql.connection.commit()
    cursor.close()

    return jsonify({'message': 'User registered successfully', '2FA Secret': twofa_secret}), 201

@auth.route('/generate_qr/<username>', methods=['GET'])
def generate_qr(username):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT twofa_secret FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()

    if not user:
        return jsonify({'error': 'User not found'}), 404

    secret = user[0]
    otp_auth_url = pyotp.totp.TOTP(secret).provisioning_uri(username, issuer_name="SecureAPI")


    qr = qrcode.make(otp_auth_url)
    img_io = io.BytesIO()
    qr.save(img_io, 'PNG')
    img_io.seek(0)

    return send_file(img_io, mimetype='image/png')

@auth.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']
    code = data.get('code')  

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, password, twofa_secret FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()

    if not user:
        return jsonify({'error': 'Invalid username or password'}), 401

    user_id, hashed_password, twofa_secret = user

    if not bcrypt.checkpw(password.encode(), hashed_password.encode()):
        return jsonify({'error': 'Invalid username or password'}), 401

    if code:
        totp = pyotp.TOTP(twofa_secret)
        if not totp.verify(code):
            return jsonify({'error': 'Invalid 2FA code'}), 401

        access_token = create_access_token(identity=str(user_id)) 
        return jsonify({'message': 'Login successful', 'token': access_token}), 200

    return jsonify({'message': 'Enter 2FA code'}), 200