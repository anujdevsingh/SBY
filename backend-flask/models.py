from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_approved = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    photo_path = db.Column(db.String(255), nullable=True)
    photo_data = db.Column(db.Text, nullable=True)  # Base64 encoded photo
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    transactions = db.relationship(
        'Transaction',
        backref='user',
        lazy=True,
        foreign_keys='Transaction.user_id'
    )
    reviewed_transactions = db.relationship(
        'Transaction',
        lazy=True,
        foreign_keys='Transaction.reviewed_by',
        primaryjoin='User.id==Transaction.reviewed_by'
    )

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'phone': self.phone,
            'photo_path': self.photo_path,
            'photo_data': self.photo_data,
            'is_admin': self.is_admin,
            'is_approved': self.is_approved,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    transaction_ref = db.Column(db.String(100), nullable=True) # Bank reference number
    screenshot_path = db.Column(db.String(255), nullable=True)
    screenshot_data = db.Column(db.Text, nullable=True)  # Base64 encoded screenshot
    user_note = db.Column(db.String(500), nullable=True)  # User's comment about the transaction
    status = db.Column(db.Enum('pending', 'approved', 'rejected', name='transaction_status', native_enum=False), default='pending', nullable=False, index=True)
    admin_note = db.Column(db.String(255), nullable=True)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'transaction_ref', name='uq_transaction_user_ref'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'amount': self.amount,
            'transaction_ref': self.transaction_ref,
            'screenshot_path': self.screenshot_path,
            'screenshot_data': self.screenshot_data,
            'user_note': self.user_note,
            'status': self.status,
            'admin_note': self.admin_note,
            'created_at': self.created_at.isoformat(),
            'user_name': self.user.full_name
        }
