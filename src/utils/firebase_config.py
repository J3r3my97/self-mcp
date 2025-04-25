import logging
import os

import firebase_admin
from firebase_admin import credentials, db, storage

from src.utils.config import settings
from src.utils.secret import get_secret

logger = logging.getLogger(__name__)

def initialize_firebase():
    """Initialize Firebase Admin SDK with service account credentials."""
    try:
        # Check if Firebase is already initialized
        if firebase_admin._apps:
            logger.info("Firebase already initialized")
            return True

        # Get project ID from environment or settings
        project_id = os.getenv('PROJECT_ID', settings.PROJECT_ID)
        if not project_id:
            logger.error("PROJECT_ID environment variable not set")
            return False

        try:
            # Get service account from Secret Manager
            service_account_info = get_secret(
                project_id=project_id,
                secret_id='firebase-service-account'
            )
            
            cred = credentials.Certificate(service_account_info)
            logger.info("Using credentials from Secret Manager")
        except Exception as e:
            logger.error(f"Error creating credentials from Secret Manager: {e}")
            return False

        # Initialize the app
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
    """Get Firebase Realtime Database instance."""
    return db

def get_storage():
    """Get Firebase Storage instance."""
    return storage 