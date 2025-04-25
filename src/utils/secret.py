import json
import logging
from typing import Any, Dict

import google.cloud.secretmanager as secretmanager

logger = logging.getLogger(__name__)

def get_secret(project_id: str, secret_id: str, version: str = "latest") -> Dict[str, Any]:
    """
    Retrieve a secret from Secret Manager.
    
    Args:
        project_id: The GCP project ID
        secret_id: The ID of the secret to retrieve
        version: The version of the secret (default: "latest")
        
    Returns:
        The secret payload as a dictionary
        
    Raises:
        Exception: If there's an error accessing the secret
    """
    try:
        # Create a Secret Manager client
        client = secretmanager.SecretManagerServiceClient()
        
        # Build the resource name of the secret version
        name = client.secret_version_path(project_id, secret_id, version)
        
        # Log the attempt
        logger.info(f"Attempting to access secret: {secret_id} from project: {project_id}")
        # Access the secret version
        response = client.access_secret_version(name=name)

        raw_payload = response.payload.data.decode("UTF-8")
        logger.info(f"Raw payload: {raw_payload}")

        # Check if payload is empty
        if not raw_payload.strip():
            logger.error("Secret payload is empty")
            raise ValueError("Secret payload is empty")
        # Parse the secret payload
        try:
            secret_payload = json.loads(raw_payload)
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing secret payload: {e}")
            logger.error(f"First 10 chars of payload: {raw_payload[:10]}...")
            raise ValueError("Invalid JSON secret payload")
        
        logger.info(f"Successfully retrieved secret: {secret_id}")
        return secret_payload
        
    except Exception as e:
        logger.error(f"Error retrieving secret {secret_id}: {e}")
        raise 