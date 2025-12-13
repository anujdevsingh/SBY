from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User
from flask import current_app
from mailer import send_email

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({"error": "Email already registered"}), 400

    hashed_pw = generate_password_hash(data.get('password'))
    new_user = User(
        email=data.get('email'),
        password_hash=hashed_pw,
        full_name=data.get('full_name'),
        phone=data.get('phone')
    )
    
    # Register endpoint should never mint additional admins; only bootstrap path creates admin
    new_user.is_admin = False
    new_user.is_active = True

    db.session.add(new_user)
    db.session.commit()

    # Notify admin of pending account
    admin_email = current_app.config.get('ADMIN_EMAIL')
    if admin_email and not new_user.is_admin:
        send_email(
            subject="SBY: New account pending approval",
            recipients=[admin_email],
            body=f"A new user registered:\nName: {new_user.full_name}\nEmail: {new_user.email}\nPhone: {new_user.phone or '-'}"
        )

    return jsonify({"message": "User registered. Please wait for admin approval."}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get('email')).first()

    if not user or not check_password_hash(user.password_hash, data.get('password')):
        return jsonify({"error": "Invalid credentials"}), 401

    if not user.is_active:
        return jsonify({"error": "Account is disabled."}), 403

    if not user.is_approved:
        return jsonify({"error": "Account not approved by admin yet."}), 403

    # PyJWT requires 'sub' (identity) to be a string
    access_token = create_access_token(identity=str(user.id))
    return jsonify({
        "access_token": access_token,
        "user": user.to_dict()
    }), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.to_dict()), 200
