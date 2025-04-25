import base64
import json
import logging
import os
from pathlib import Path

import firebase_admin
from firebase_admin import credentials, db, storage

from src.utils.config import settings

logger = logging.getLogger(__name__)

def initialize_firebase():
    """Initialize Firebase Admin SDK with service account credentials."""
    try:
        # Check if Firebase is already initialized
        if firebase_admin._apps:
            logger.info("Firebase already initialized")
            return True

        # Try to get credentials from environment variable first
        cred_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if cred_path and os.path.exists(cred_path):
            try:
                cred = credentials.Certificate(cred_path)
                logger.info(f"Using credentials from file: {cred_path}")
            except Exception as e:
                logger.error(f"Error creating credentials from file: {e}")
                return False
        # Fall back to service account from settings
        elif settings.FIREBASE_SERVICE_ACCOUNT:
            try:
                cred = credentials.Certificate(settings.FIREBASE_SERVICE_ACCOUNT)
                logger.info("Using credentials from settings")
            except Exception as e:
                logger.error(f"Error creating credentials from service account: {e}")
                return False
        else:
            logger.error("No Firebase credentials found")
            logger.error("Please provide either GOOGLE_APPLICATION_CREDENTIALS environment variable or FIREBASE_SERVICE_ACCOUNT in settings")
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