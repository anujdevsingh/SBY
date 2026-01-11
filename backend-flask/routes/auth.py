import os
import uuid
import base64
from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User
from mailer import send_email

auth_bp = Blueprint('auth', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def file_to_base64(file):
    """Convert uploaded file to Base64 data URI."""
    if not file or not file.filename:
        return None
    
    # Read file content
    content = file.read()
    file.seek(0)  # Reset file pointer
    
    # Get MIME type
    ext = file.filename.rsplit('.', 1)[1].lower()
    mime_types = {
        'png': 'image/png',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'gif': 'image/gif',
        'webp': 'image/webp'
    }
    mime = mime_types.get(ext, 'image/jpeg')
    
    # Encode to base64
    b64 = base64.b64encode(content).decode('utf-8')
    return f"data:{mime};base64,{b64}"

@auth_bp.route('/register', methods=['POST'])
def register():
    # Handle both JSON and FormData
    if request.content_type and 'multipart/form-data' in request.content_type:
        data = request.form.to_dict()
        photo = request.files.get('photo')
    else:
        data = request.get_json()
        photo = None
    
    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({"error": "Email already registered"}), 400

    hashed_pw = generate_password_hash(data.get('password'))
    
    # Handle photo upload - convert to Base64
    photo_data = None
    if photo and photo.filename and allowed_file(photo.filename):
        photo_data = file_to_base64(photo)
    
    new_user = User(
        email=data.get('email'),
        password_hash=hashed_pw,
        full_name=data.get('full_name'),
        phone=data.get('phone'),
        photo_data=photo_data
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

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update current user's profile including photo."""
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Handle both JSON and FormData
    if request.content_type and 'multipart/form-data' in request.content_type:
        data = request.form.to_dict()
        photo = request.files.get('photo')
    else:
        data = request.get_json() or {}
        photo = None
    
    # Update basic fields
    if 'full_name' in data and data['full_name']:
        user.full_name = data['full_name']
    if 'phone' in data:
        user.phone = data['phone']
    
    # Handle password change
    if 'new_password' in data and data['new_password']:
        if 'current_password' not in data:
            return jsonify({"error": "Current password required to change password"}), 400
        if not check_password_hash(user.password_hash, data['current_password']):
            return jsonify({"error": "Current password is incorrect"}), 400
        user.password_hash = generate_password_hash(data['new_password'])
    
    # Handle photo upload - convert to Base64
    if photo and photo.filename and allowed_file(photo.filename):
        user.photo_data = file_to_base64(photo)
    
    db.session.commit()
    
    return jsonify({
        "message": "Profile updated successfully",
        "user": user.to_dict()
    }), 200
