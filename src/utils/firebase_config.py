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

        # Get service account from settings
        if settings.FIREBASE_SERVICE_ACCOUNT:
            try:
                cred = credentials.Certificate(settings.FIREBASE_SERVICE_ACCOUNT)
            except Exception as e:
                logger.error(f"Error creating credentials from service account: {e}")
                return False
        else:
            logger.error("Firebase service account not found in settings")
            logger.error("Please provide FIREBASE_SERVICE_ACCOUNT environment variable")
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