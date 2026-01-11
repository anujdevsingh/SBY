import os
import uuid
import base64
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from sqlalchemy import or_
from models import db, Transaction, User
from mailer import send_email

transactions_bp = Blueprint('transactions', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

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


@transactions_bp.route('/summary', methods=['GET'])
def donation_summary():
    """
    Public-friendly aggregate of approved donations for dashboards.
    """
    total_amount = db.session.query(db.func.sum(Transaction.amount)).filter_by(status='approved').scalar() or 0
    total_count = Transaction.query.filter_by(status='approved').count()
    return jsonify({
        "total_amount": total_amount,
        "approved_count": total_count
    }), 200


@transactions_bp.route('/top-donators', methods=['GET'])
def top_donators():
    """
    Public endpoint returning top 5 donors with name, photo, and total approved donations.
    """
    # Get top donors with total approved donations
    top_donors = db.session.query(
        User.id,
        User.full_name,
        User.photo_path,
        User.photo_data,
        db.func.sum(Transaction.amount).label('total_donated')
    ).join(Transaction, User.id == Transaction.user_id)\
     .filter(Transaction.status == 'approved')\
     .group_by(User.id, User.full_name, User.photo_path, User.photo_data)\
     .order_by(db.func.sum(Transaction.amount).desc())\
     .limit(5)\
     .all()
    
    result = []
    for donor in top_donors:
        result.append({
            "id": donor.id,
            "name": donor.full_name,
            "photo_path": donor.photo_path,
            "photo_data": donor.photo_data,
            "total_donated": float(donor.total_donated) if donor.total_donated else 0
        })
    
    return jsonify(result), 200


@transactions_bp.route('/', methods=['POST'])
@jwt_required()
def create_transaction():
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    
    if 'screenshot' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['screenshot']
    amount = request.form.get('amount')
    ref = request.form.get('transaction_ref')
    user_note = request.form.get('user_note', '')  # Optional comment from user

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if file and allowed_file(file.filename):
        # Convert screenshot to Base64
        screenshot_data = file_to_base64(file)
        
        new_tx = Transaction(
            user_id=current_user_id,
            amount=float(amount),
            transaction_ref=ref,
            screenshot_data=screenshot_data,
            user_note=user_note if user_note else None
        )
        db.session.add(new_tx)
        db.session.commit()
        
        # Notify Admin
        admin_email = current_app.config.get('ADMIN_EMAIL')
        if admin_email:
            note_line = f"\nUser note: {user_note}" if user_note else ""
            send_email(
                subject="SBY: New transaction pending review",
                recipients=[admin_email],
                body=f"User {user.full_name} ({user.email}) submitted a transaction of ₹{amount} with ref {ref}.{note_line}"
            )
        
        return jsonify({"message": "Transaction submitted successfully"}), 201

    return jsonify({"error": "Invalid file type"}), 400

@transactions_bp.route('/', methods=['GET'])
@jwt_required()
def get_my_transactions():
    current_user_id = int(get_jwt_identity())
    transactions = Transaction.query.filter_by(user_id=current_user_id).order_by(Transaction.created_at.desc()).all()
    return jsonify([t.to_dict() for t in transactions]), 200

# Admin Transaction Management
@transactions_bp.route('/admin/all', methods=['GET'])
@jwt_required()
def get_all_transactions():
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    if not user.is_admin:
        return jsonify({"error": "Unauthorized"}), 403
    
    status = request.args.get('status')
    search = request.args.get('q')
    user_id = request.args.get('user_id')

    query = Transaction.query.join(User, Transaction.user_id == User.id)

    if status:
        query = query.filter(Transaction.status == status)
    if user_id:
        query = query.filter(Transaction.user_id == user_id)
    if search:
        like_expr = f"%{search}%"
        query = query.filter(
            or_(
                Transaction.transaction_ref.ilike(like_expr),
                User.email.ilike(like_expr),
                User.full_name.ilike(like_expr)
            )
        )
        
    transactions = query.order_by(Transaction.created_at.desc()).all()
    return jsonify([t.to_dict() for t in transactions]), 200

@transactions_bp.route('/<int:tx_id>/status', methods=['POST'])
@jwt_required()
def update_transaction_status(tx_id):
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    if not user.is_admin:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    new_status = data.get('status') # approved, rejected
    note = data.get('note', '')

    if new_status not in ['approved', 'rejected']:
        return jsonify({"error": "Invalid status"}), 400

    tx = Transaction.query.get_or_404(tx_id)
    tx.status = new_status
    tx.admin_note = note
    tx.reviewed_by = current_user_id
    tx.reviewed_at = datetime.utcnow()
    db.session.commit()
    
    # Notify User
    recipient = tx.user.email if tx.user else None
    if recipient:
        note_line = f"\nNote from admin: {note}" if note else ""
        send_email(
            subject=f"Your transaction was {new_status}",
            recipients=[recipient],
            body=f"Hello,\n\nYour transaction #{tx.id} has been {new_status}.{note_line}\n"
        )

    return jsonify({"message": f"Transaction {new_status}"}), 200
