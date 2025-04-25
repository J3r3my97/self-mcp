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

        # Get credentials from environment variable
        service_account_json = os.getenv('FIREBASE_SERVICE_ACCOUNT')
        if not service_account_json:
            logger.error("FIREBASE_SERVICE_ACCOUNT environment variable not set")
            return False

        try:
            # Use the Settings class's parse_service_account function
            service_account_info = settings.parse_service_account(service_account_json)
            if not service_account_info:
                logger.error("Failed to parse FIREBASE_SERVICE_ACCOUNT")
                return False

            cred = credentials.Certificate(service_account_info)
            logger.info("Using credentials from FIREBASE_SERVICE_ACCOUNT environment variable")
        except Exception as e:
            logger.error(f"Error creating credentials from FIREBASE_SERVICE_ACCOUNT: {e}")
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