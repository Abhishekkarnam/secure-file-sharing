from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token
from database.models import User, db
from logs.logger import log_event

auth_bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        log_event(username or 'unknown', 'User Registration', 'FAILED')
        return jsonify({"msg": "Username and password are required"}), 400

    if User.query.filter_by(username=username).first():
        log_event(username, 'User Registration', 'FAILED')
        return jsonify({"msg": "Username already exists"}), 409

    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, password=hashed_pw)
    db.session.add(new_user)
    db.session.commit()
    log_event(username, 'User Registration', 'SUCCESS')
    return jsonify({"msg": "User created"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first() if username else None
    if user and bcrypt.check_password_hash(user.password, password):
        token = create_access_token(
            identity=user.username,
            additional_claims={"role": user.role}
        )
        log_event(user.username, 'User Login', 'SUCCESS')
        return jsonify(access_token=token, role=user.role, username=user.username), 200

    log_event(username or 'unknown', 'User Login', 'FAILED')
    return jsonify({"msg": "Invalid credentials"}), 401
