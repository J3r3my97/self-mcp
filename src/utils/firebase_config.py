import firebase_admin
from firebase_admin import credentials, db, storage

from ..utils.config import settings


def initialize_firebase():
    """Initialize Firebase Admin SDK with service account credentials."""
    try:
        # Initialize the app with service account credentials
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred, {
            'databaseURL': settings.FIREBASE_DATABASE_URL,
            'storageBucket': settings.FIREBASE_STORAGE_BUCKET
        })
        return True
    except Exception as e:
        print(f"Error initializing Firebase: {e}")
        return False

def get_database():
    """Get Firebase Realtime Database reference."""
    return db.reference()

def get_storage():
    """Get Firebase Storage bucket reference."""
    return storage.bucket() 