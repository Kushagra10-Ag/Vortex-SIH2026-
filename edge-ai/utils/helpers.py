"""
Utility Helper Functions for Edge-AI Module
UUID generation, timestamps, math helpers, file I/O, JSON serialization
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import os


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# UUID & ID GENERATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def generate_event_id() -> str:
    """
    Generate unique event ID
    
    Returns:
        str: UUID v4 string (36 characters)
    """
    return str(uuid.uuid4())


def generate_device_id() -> str:
    """
    Generate unique device ID (shorter than UUID)
    
    Returns:
        str: 12-character hex string
    """
    return uuid.uuid4().hex[:12]


def generate_frame_id() -> str:
    """
    Generate unique frame ID for tracking
    
    Returns:
        str: UUID v4 string
    """
    return str(uuid.uuid4())


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TIMESTAMP UTILITIES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_utc_timestamp() -> str:
    """
    Get current UTC timestamp in ISO 8601 format
    
    Returns:
        str: ISO format timestamp (e.g., "2025-12-25T15:30:45.123456Z")
    """
    return datetime.now(timezone.utc).isoformat()


def get_utc_timestamp_ms() -> int:
    """
    Get current UTC timestamp in milliseconds since epoch
    
    Returns:
        int: Milliseconds since epoch
    """
    return int(datetime.now(timezone.utc).timestamp() * 1000)


def timestamp_to_iso(timestamp_ms: int) -> str:
    """
    Convert millisecond timestamp to ISO format
    
    Args:
        timestamp_ms: Milliseconds since epoch
    
    Returns:
        str: ISO format string
    """
    return datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc).isoformat()


def parse_iso_timestamp(iso_str: str) -> datetime:
    """
    Parse ISO format timestamp string
    
    Args:
        iso_str: ISO format string
    
    Returns:
        datetime: Parsed datetime object
    """
    return datetime.fromisoformat(iso_str.replace('Z', '+00:00'))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MATH & CALCULATION HELPERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def distance_euclidean(p1: tuple, p2: tuple) -> float:
    """
    Calculate Euclidean distance between two 2D points
    
    Args:
        p1: (x1, y1) tuple
        p2: (x2, y2) tuple
    
    Returns:
        float: Distance in pixels
    """
    x1, y1 = p1
    x2, y2 = p2
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5


def bounding_box_area(bbox: List[int]) -> int:
    """
    Calculate area of bounding box
    
    Args:
        bbox: [x, y, width, height]
    
    Returns:
        int: Area in square pixels
    """
    if len(bbox) != 4:
        return 0
    x, y, w, h = bbox
    return max(0, w * h)


def bounding_box_center(bbox: List[int]) -> tuple:
    """
    Calculate center point of bounding box
    
    Args:
        bbox: [x, y, width, height]
    
    Returns:
        tuple: (center_x, center_y)
    """
    if len(bbox) != 4:
        return (0, 0)
    x, y, w, h = bbox
    return (x + w // 2, y + h // 2)


def normalize_confidence(score: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    """
    Normalize confidence score to range [0, 1]
    
    Args:
        score: Raw confidence score
        min_val: Minimum expected value
        max_val: Maximum expected value
    
    Returns:
        float: Normalized score between 0.0 and 1.0
    """
    if max_val <= min_val:
        return 0.0
    normalized = (score - min_val) / (max_val - min_val)
    return max(0.0, min(1.0, normalized))


def percentage(part: float, whole: float, precision: int = 2) -> float:
    """
    Calculate percentage
    
    Args:
        part: Part value
        whole: Total/whole value
        precision: Decimal places
    
    Returns:
        float: Percentage value
    """
    if whole == 0:
        return 0.0
    return round((part / whole) * 100, precision)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# JSON SERIALIZATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def to_json_serializable(obj: Any) -> Any:
    """
    Convert object to JSON-serializable format
    Handles datetime, UUID, and custom objects
    
    Args:
        obj: Object to convert
    
    Returns:
        JSON-serializable object
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, uuid.UUID):
        return str(obj)
    elif isinstance(obj, dict):
        return {k: to_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [to_json_serializable(item) for item in obj]
    return obj


def dict_to_json(data: Dict) -> str:
    """
    Convert dictionary to JSON string
    
    Args:
        data: Dictionary to convert
    
    Returns:
        str: JSON string
    """
    return json.dumps(to_json_serializable(data), ensure_ascii=False, indent=2)


def json_to_dict(json_str: str) -> Dict:
    """
    Parse JSON string to dictionary
    
    Args:
        json_str: JSON string
    
    Returns:
        dict: Parsed dictionary
    """
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FILE I/O HELPERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def ensure_directory(path: str) -> bool:
    """
    Ensure directory exists, create if necessary
    
    Args:
        path: Directory path
    
    Returns:
        bool: True if directory exists or was created
    """
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except OSError as e:
        return False


def save_json_file(data: Dict, filepath: str) -> bool:
    """
    Save dictionary as JSON file
    
    Args:
        data: Dictionary to save
        filepath: Path to save file
    
    Returns:
        bool: True if successful
    """
    try:
        # Ensure directory exists
        directory = os.path.dirname(filepath)
        if directory:
            ensure_directory(directory)
        
        with open(filepath, 'w') as f:
            json.dump(to_json_serializable(data), f, indent=2, ensure_ascii=False)
        return True
    except IOError as e:
        return False


def load_json_file(filepath: str) -> Optional[Dict]:
    """
    Load JSON file as dictionary
    
    Args:
        filepath: Path to JSON file
    
    Returns:
        dict or None: Loaded dictionary or None if failed
    """
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError):
        return None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# VALIDATION HELPERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def is_valid_bbox(bbox: Any) -> bool:
    """
    Validate bounding box format [x, y, width, height]
    
    Args:
        bbox: Bounding box data
    
    Returns:
        bool: True if valid
    """
    if not isinstance(bbox, (list, tuple)) or len(bbox) != 4:
        return False
    x, y, w, h = bbox
    return all(isinstance(v, (int, float)) and v >= 0 for v in [x, y, w, h])


def is_valid_confidence(confidence: float) -> bool:
    """
    Validate confidence score (should be 0.0 to 1.0)
    
    Args:
        confidence: Confidence score
    
    Returns:
        bool: True if valid
    """
    return isinstance(confidence, (int, float)) and 0.0 <= confidence <= 1.0


def clamp(value: float, min_val: float, max_val: float) -> float:
    """
    Clamp value to range [min_val, max_val]
    
    Args:
        value: Value to clamp
        min_val: Minimum bound
        max_val: Maximum bound
    
    Returns:
        float: Clamped value
    """
    return max(min_val, min(max_val, value))
