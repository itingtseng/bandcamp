import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default_secret_key')  # Default fallback
    FLASK_RUN_PORT = os.environ.get('FLASK_RUN_PORT', 5000)  # Default port fallback
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True

    # Handle missing or improperly formatted DATABASE_URL
    DATABASE_URL = os.environ.get('DATABASE_URL', '')  # Default to an empty string
    if DATABASE_URL.startswith('postgres://'):  # Replace deprecated 'postgres://' prefix
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://')

    # Fallback to SQLite if DATABASE_URL is not set
    SQLALCHEMY_DATABASE_URI = DATABASE_URL or 'sqlite:///app.db'
