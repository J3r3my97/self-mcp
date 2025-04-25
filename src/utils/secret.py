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
        
        # Access the secret version
        response = client.access_secret_version(name=name)
        
        # Parse the secret payload
        secret_payload = json.loads(response.payload.data.decode("UTF-8"))
        
        logger.info(f"Successfully retrieved secret: {secret_id}")
        return secret_payload
        
    except Exception as e:
        logger.error(f"Error retrieving secret {secret_id}: {e}")
        raise 