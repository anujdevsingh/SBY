from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Transaction
from mailer import send_email

admin_bp = Blueprint('admin', __name__)

def is_admin(user_id):
    user = User.query.get(int(user_id))
    return user and user.is_admin

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    current_user_id = int(get_jwt_identity())
    if not is_admin(current_user_id):
        return jsonify({"error": "Unauthorized"}), 403

    status_filter = request.args.get('pending')
    query = User.query
    if status_filter == 'true':
        query = query.filter_by(is_approved=False)
    
    users = query.all()
    
    # Build result with total donated amount for each user
    result = []
    for user in users:
        user_data = user.to_dict()
        # Calculate total donated (approved transactions only)
        total_donated = db.session.query(db.func.sum(Transaction.amount))\
            .filter(Transaction.user_id == user.id, Transaction.status == 'approved')\
            .scalar() or 0
        user_data['total_donated'] = float(total_donated)
        result.append(user_data)
    
    return jsonify(result), 200

@admin_bp.route('/users/<int:user_id>/approve', methods=['POST'])
@jwt_required()
def approve_user(user_id):
    current_user_id = int(get_jwt_identity())
    if not is_admin(current_user_id):
        return jsonify({"error": "Unauthorized"}), 403

    user = User.query.get_or_404(user_id)
    user.is_approved = True
    db.session.commit()
    
    send_email(
        subject="Your Sahyog Bima Yojna account is approved",
        recipients=[user.email],
        body="Hello,\n\nYour account has been approved. You can now log in and submit your contribution proofs.\n\nThank you."
    )

    return jsonify({"message": "User approved"}), 200

@admin_bp.route('/users/<int:user_id>/reject', methods=['POST'])
@jwt_required()
def reject_user(user_id):
    current_user_id = int(get_jwt_identity())
    if not is_admin(current_user_id):
        return jsonify({"error": "Unauthorized"}), 403

    user = User.query.get_or_404(user_id)
    user.is_approved = False
    user.is_active = False
    db.session.commit()

    send_email(
        subject="Your Sahyog Bima Yojna account was rejected",
        recipients=[user.email],
        body="Hello,\n\nYour account request was rejected/disabled. If you believe this is an error, please contact the administrator.\n"
    )

    return jsonify({"message": "User rejected and disabled"}), 200

@admin_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    current_user_id = int(get_jwt_identity())
    if not is_admin(current_user_id):
        return jsonify({"error": "Unauthorized"}), 403

    total_donations = db.session.query(db.func.sum(Transaction.amount)).filter_by(status='approved').scalar() or 0
    total_users = User.query.count()
    pending_users = User.query.filter_by(is_approved=False).count()
    pending_transactions = Transaction.query.filter_by(status='pending').count()

    return jsonify({
        "total_donations": total_donations,
        "total_users": total_users,
        "pending_users": pending_users,
        "pending_transactions": pending_transactions
    }), 200
