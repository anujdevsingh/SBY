import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-123'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///sby.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@sby.local')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'change-me-now')
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'false').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', ADMIN_EMAIL)
    MAIL_SUPPRESS_SEND = os.environ.get('MAIL_SUPPRESS_SEND', 'false').lower() == 'true'
    POLICY_INDEX_PATH = os.environ.get('POLICY_INDEX_PATH', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'policy_store', 'policy.index'))
    POLICY_META_PATH = os.environ.get('POLICY_META_PATH', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'policy_store', 'policy_meta.json'))
    POLICY_EMBED_MODEL = os.environ.get('POLICY_EMBED_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
