import logging
import os
from pathlib import Path

import firebase_admin
from firebase_admin import credentials, db, storage

from utils.config import settings

logger = logging.getLogger(__name__)

def initialize_firebase():
    """Initialize Firebase Admin SDK with service account credentials."""
    try:
        # Check if Firebase is already initialized
        if firebase_admin._apps:
            logger.info("Firebase already initialized")
            return True

        # Get absolute path to service account key
        project_root = Path(__file__).parent.parent.parent
        service_account_path = project_root / "serviceAccountKey.json"
        
        if not service_account_path.exists():
            logger.error(f"Firebase service account key file not found at {service_account_path}")
            logger.error("Please download your service account key from Firebase Console and save it as serviceAccountKey.json")
            return False

        # Initialize the app with service account credentials
        cred = credentials.Certificate(str(service_account_path))
        firebase_admin.initialize_app(cred, {
            'databaseURL': settings.FIREBASE_DATABASE_URL,
            'storageBucket': settings.FIREBASE_STORAGE_BUCKET
        })
        logger.info("Firebase initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Error initializing Firebase: {e}")
        return False

def get_database():
    """Get Firebase Realtime Database reference."""
    return db.reference()

def get_storage():
    """Get Firebase Storage bucket reference."""
    return storage.bucket() 