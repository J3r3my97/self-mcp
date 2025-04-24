import base64
import json
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

        # Get service account from environment variable if available
        service_account_json = os.getenv('FIREBASE_SERVICE_ACCOUNT')
        if service_account_json:
            try:
                # Decode base64 if it's encoded
                if service_account_json.startswith('base64:'):
                    service_account_json = base64.b64decode(service_account_json[7:]).decode('utf-8')
                
                # Parse the JSON
                service_account = json.loads(service_account_json)
                cred = credentials.Certificate(service_account)
            except Exception as e:
                logger.error(f"Error parsing service account from environment: {e}")
                return False
        else:
            # Fall back to file-based approach
            project_root = Path(__file__).parent.parent.parent
            service_account_path = project_root / "serviceAccountKey.json"
            
            if not service_account_path.exists():
                logger.error(f"Firebase service account key file not found at {service_account_path}")
                logger.error("Please provide FIREBASE_SERVICE_ACCOUNT environment variable or serviceAccountKey.json file")
                return False

            cred = credentials.Certificate(str(service_account_path))

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
    """Get Firebase Realtime Database reference."""
    return db.reference()

def get_storage():
    """Get Firebase Storage bucket reference."""
    return storage.bucket() 