import logging
import os
import sys
from pathlib import Path

from torchvision.models.detection import fasterrcnn_resnet50_fpn_v2
from transformers import ViTFeatureExtractor, ViTModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def download_models():
    """Download and cache all necessary model files."""
    try:
        # Set cache directory
        cache_dir = os.getenv("TRANSFORMERS_CACHE", "/app/models")
        cache_path = Path(cache_dir)
        cache_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"Downloading models to {cache_dir}")

        # Download ViT model and feature extractor
        try:
            logger.info("Downloading ViT model...")
            ViTModel.from_pretrained(
                "google/vit-base-patch16-224",
                cache_dir=cache_dir,
                local_files_only=False,
                force_download=True,
            )
            logger.info("ViT model downloaded successfully")

            logger.info("Downloading ViT feature extractor...")
            ViTFeatureExtractor.from_pretrained(
                "google/vit-base-patch16-224",
                cache_dir=cache_dir,
                local_files_only=False,
                force_download=True,
            )
            logger.info("ViT feature extractor downloaded successfully")
        except Exception as e:
            logger.error(f"Error downloading ViT models: {str(e)}")
            raise

        # Download Faster R-CNN model
        try:
            logger.info("Downloading Faster R-CNN model...")
            fasterrcnn_resnet50_fpn_v2(pretrained=True)
            logger.info("Faster R-CNN model downloaded successfully")
        except Exception as e:
            logger.error(f"Error downloading Faster R-CNN model: {str(e)}")
            raise

        # Verify models were downloaded
        model_files = list(cache_path.glob("**/*"))
        if not model_files:
            raise RuntimeError("No model files were downloaded")
        
        logger.info(f"Found {len(model_files)} model files")
        for file in model_files:
            logger.info(f"Model file: {file}")

        logger.info("All models downloaded successfully")

    except Exception as e:
        logger.error(f"Error downloading models: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    download_models()
