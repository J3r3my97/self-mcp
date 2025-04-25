import io
import logging
import os
import time
from typing import Any, Dict, List

import numpy as np
import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as T
import torchvision.transforms.functional as F
from PIL import Image
from torchvision.models.detection import fasterrcnn_resnet50_fpn_v2
from transformers import ViTFeatureExtractor, ViTModel

from src.utils.config import settings

logger = logging.getLogger(__name__)


class FashionDetector:
    def __init__(self, device=None):
        """Initialize the fashion detector with object detection and feature extraction models."""
        self.device = (
            device
            if device
            else torch.device("cuda" if torch.cuda.is_available() else "cpu")
        )
        logger.info(f"Using device: {self.device}")

        try:
            # Initialize object detection model
            logger.info("Loading object detection model...")
            self.detector = fasterrcnn_resnet50_fpn_v2(pretrained=True)
            self.detector.to(self.device)
            self.detector.eval()

            # Initialize feature extractor
            logger.info("Loading ViT model...")
            model_path = os.path.join(os.path.dirname(__file__), "huggingface_models")
            os.makedirs(model_path, exist_ok=True)
            self.feature_extractor = ViTModel.from_pretrained(
                "google/vit-base-patch16-224",
                cache_dir=model_path,
                local_files_only=False,
            )
            self.feature_processor = ViTFeatureExtractor.from_pretrained(
                "google/vit-base-patch16-224",
                cache_dir=model_path,
                local_files_only=False,
            )
            self.feature_extractor.to(self.device)
            self.feature_extractor.eval()

            # Initialize linear layers for attribute prediction
            logger.info("Initializing classifiers...")
            self.category_classifier = nn.Linear(768, 50).to(
                self.device
            )  # 50 fashion categories
            self.attribute_classifier = nn.Linear(768, 100).to(
                self.device
            )  # 100 attributes

            logger.info("Model initialization completed successfully")

        except Exception as e:
            logger.error(f"Error initializing models: {str(e)}")
            raise RuntimeError(f"Failed to initialize models: {str(e)}")

    def preprocess_image(self, image_data):
        """
        Preprocess image for model input.

        Args:
            image_data: bytes, PIL Image, or numpy array

        Returns:
            torch.Tensor: Preprocessed image tensor
        """
        if isinstance(image_data, bytes):
            image = Image.open(io.BytesIO(image_data))
        elif isinstance(image_data, np.ndarray):
            image = Image.fromarray(image_data)
        elif isinstance(image_data, Image.Image):
            image = image_data
        else:
            raise ValueError("image_data must be bytes, PIL Image, or numpy array")

        # Convert to RGB if needed
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Convert to tensor and normalize
        image_tensor = F.to_tensor(image)
        image_tensor = F.normalize(
            image_tensor, mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
        )
        return image_tensor.unsqueeze(0)

    def forward(self, image_data):
        """
        Process image through object detection model.

        Args:
            image_data: bytes, PIL Image, or numpy array

        Returns:
            list: List of detected objects with bounding boxes and scores
        """
        with torch.no_grad():
            image_tensor = self.preprocess_image(image_data)
            image_tensor = image_tensor.to(self.device)
            detections = self.detector(image_tensor)[0]

            # Filter detections with confidence > 0.5
            mask = detections["scores"] > 0.5
            boxes = detections["boxes"][mask].cpu().numpy()
            scores = detections["scores"][mask].cpu().numpy()

            results = []
            for box, score in zip(boxes, scores):
                results.append({"box": box.tolist(), "confidence": float(score)})
            return results

    def get_embeddings(self, image_data):
        """
        Get embeddings for a single image.

        Args:
            image_data: bytes, PIL Image, or numpy array

        Returns:
            list: Feature embeddings as a list of floats
        """
        if isinstance(image_data, bytes):
            image = Image.open(io.BytesIO(image_data))
        elif isinstance(image_data, np.ndarray):
            image = Image.fromarray(image_data)
        elif isinstance(image_data, Image.Image):
            image = image_data
        else:
            raise ValueError("image_data must be bytes, PIL Image, or numpy array")

        # Convert to RGB if needed
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Process image for feature extraction
        inputs = self.feature_processor(images=image, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.feature_extractor(**inputs)
            embeddings = outputs.pooler_output.cpu().numpy()

        return embeddings[0].tolist()  # Convert numpy array to list and return

    def check_status(self) -> Dict[str, Any]:
        """Check model status and health."""
        try:
            # Check if models are loaded
            detector_loaded = hasattr(self, "detector") and self.detector is not None
            vit_loaded = hasattr(self, "vit_model") and self.vit_model is not None

            # Try a small forward pass
            if detector_loaded and vit_loaded:
                test_input = torch.randn(1, 3, 224, 224).to(self.device)
                with torch.no_grad():
                    self.detector(test_input)
                    self.vit_model(test_input)

            return {
                "status": "healthy",
                "details": {
                    "device": str(self.device),
                    "detector_loaded": detector_loaded,
                    "vit_loaded": vit_loaded,
                    "memory_allocated": torch.cuda.memory_allocated()
                    if self.device == "cuda"
                    else 0,
                },
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
