import os
from dotenv import load_dotenv

# IMPORTANT: Load .env BEFORE importing Config so environment variables are available
load_dotenv()

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from sqlalchemy import inspect
from config import Config
from models import db
from werkzeug.security import generate_password_hash
from models import User
from extensions import mail


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Convert Windows path separators to standard if needed, mostly handled by python
    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Extensions
    CORS(app)
    db.init_app(app)
    Migrate(app, db)
    JWTManager(app)
    mail.init_app(app)

    # Seed a default admin if none exists
    with app.app_context():
        try:
            inspector = inspect(db.engine)
            # Auto-create tables if they don't exist (no need to run flask db upgrade manually)
            if not inspector.has_table('user'):
                print("Creating database tables...")
                db.create_all()
                print("Database tables created successfully!")
            
            if not User.query.filter_by(is_admin=True).first():
                admin = User(
                    email=app.config['ADMIN_EMAIL'],
                    password_hash=generate_password_hash(app.config['ADMIN_PASSWORD']),
                    full_name='Administrator',
                    phone='',
                    is_admin=True,
                    is_approved=True,
                    is_active=True
                )
                db.session.add(admin)
                db.session.commit()
                print(f"DEFAULT ADMIN CREATED -> email: {admin.email}")
        except Exception as exc:  # pragma: no cover - best-effort bootstrap
            print(f"Skipping default admin creation: {exc}")

    # Register Blueprints
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.transactions import transactions_bp
    from routes.policy import policy_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(transactions_bp, url_prefix='/api/transactions')
    app.register_blueprint(policy_bp, url_prefix='/api/policy')

    # Serve uploads
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    @app.route('/')
    def index():
        return jsonify({"message": "Sahyog Bima Yojna API is running"})

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
