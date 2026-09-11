"""
AI Package — YOLO inference, people detection, queue detection, shelf detection, and tracking
"""

from .inference import InferenceEngine, filter_persons, highest_confidence
from .model_loader import ModelLoader
from .people_detector import PeopleDetector
from .queue_detector import QueueDetector
from .shelf_detector import ShelfDetector, create_default_shelf_configs, ShelfConfig
from .tracker import CentroidTracker, TrackState

__all__ = [
    "ModelLoader",
    "InferenceEngine",
    "filter_persons",
    "highest_confidence",
    "PeopleDetector",
    "QueueDetector",
    "ShelfDetector",
    "create_default_shelf_configs",
    "ShelfConfig",
    "CentroidTracker",
    "TrackState",
]
