import io
from typing import Any, Dict, List

import numpy as np
import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as T
import torchvision.transforms.functional as F
from PIL import Image
from torchvision.models.detection import fasterrcnn_resnet50_fpn_v2
from transformers import ViTImageProcessor, ViTModel

from ..utils.config import settings


class FashionDetector:
    def __init__(self, device=None):
        """Initialize the fashion detector with object detection and feature extraction models."""
        self.device = device if device else torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Initialize object detection model
        self.detector = fasterrcnn_resnet50_fpn_v2(pretrained=True)
        self.detector.to(self.device)
        self.detector.eval()
        
        # Initialize feature extractor
        self.feature_extractor = ViTModel.from_pretrained('google/vit-base-patch16-224')
        self.feature_processor = ViTImageProcessor.from_pretrained('google/vit-base-patch16-224')
        self.feature_extractor.to(self.device)
        self.feature_extractor.eval()
        
        # Initialize linear layers for attribute prediction
        self.category_classifier = nn.Linear(768, 50).to(self.device)  # 50 fashion categories
        self.attribute_classifier = nn.Linear(768, 100).to(self.device)  # 100 attributes

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
        if image.mode != 'RGB':
            image = image.convert('RGB')
            
        # Convert to tensor and normalize
        image_tensor = F.to_tensor(image)
        image_tensor = F.normalize(image_tensor, 
                                 mean=[0.485, 0.456, 0.406], 
                                 std=[0.229, 0.224, 0.225])
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
            mask = detections['scores'] > 0.5
            boxes = detections['boxes'][mask].cpu().numpy()
            scores = detections['scores'][mask].cpu().numpy()
            
            results = []
            for box, score in zip(boxes, scores):
                results.append({
                    'box': box.tolist(),
                    'confidence': float(score)
                })
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
        if image.mode != 'RGB':
            image = image.convert('RGB')
            
        # Process image for feature extraction
        inputs = self.feature_processor(images=image, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.feature_extractor(**inputs)
            embeddings = outputs.pooler_output.cpu().numpy()
            
        return embeddings[0].tolist()  # Convert numpy array to list and return 