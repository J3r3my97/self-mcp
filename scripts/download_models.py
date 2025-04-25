import logging
import os

from torchvision.models.detection import fasterrcnn_resnet50_fpn_v2
from transformers import ViTFeatureExtractor, ViTModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def download_models():
    """Download and cache all necessary model files."""
    try:
        # Set cache directory
        cache_dir = os.getenv("TRANSFORMERS_CACHE", "/app/models")
        os.makedirs(cache_dir, exist_ok=True)

        logger.info(f"Downloading models to {cache_dir}")

        # Download ViT model and feature extractor
        logger.info("Downloading ViT model...")
        ViTModel.from_pretrained(
            "google/vit-base-patch16-224", cache_dir=cache_dir, local_files_only=False
        )

        logger.info("Downloading ViT feature extractor...")
        ViTFeatureExtractor.from_pretrained(
            "google/vit-base-patch16-224", cache_dir=cache_dir, local_files_only=False
        )

        # Download Faster R-CNN model
        logger.info("Downloading Faster R-CNN model...")
        fasterrcnn_resnet50_fpn_v2(pretrained=True)

        logger.info("All models downloaded successfully")

    except Exception as e:
        logger.error(f"Error downloading models: {str(e)}")
        raise


if __name__ == "__main__":
    download_models()
