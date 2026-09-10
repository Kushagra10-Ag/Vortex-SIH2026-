"""
Edge-AI Utils Module — Re-exports all utility components
Provides centralized access to logging, helpers, image processing, and constants
"""

# Import all constants
from .constants import (
    CameraEventType,
    DetectorType,
    SensorType,
    DeviceStatus,
    AlertSeverity,
    AlertCategory,
    ShelfStockStatus,
    ModelConfig,
    SensorThresholds,
    CameraConfig,
    CommunicationConfig,
    LogConfig,
)

# Import logger
from .logger import EdgeAILogger, logger, log_debug, log_info, log_warning, log_error, log_critical, log_exception

# Import helpers
from .helpers import (
    generate_event_id,
    generate_device_id,
    generate_frame_id,
    get_utc_timestamp,
    get_utc_timestamp_ms,
    timestamp_to_iso,
    parse_iso_timestamp,
    distance_euclidean,
    bounding_box_area,
    bounding_box_center,
    normalize_confidence,
    percentage,
    to_json_serializable,
    dict_to_json,
    json_to_dict,
    ensure_directory,
    save_json_file,
    load_json_file,
    is_valid_bbox,
    is_valid_confidence,
    clamp,
)

# Import image utilities
from .image_utils import (
    resize_frame,
    normalize_frame,
    bgr_to_rgb,
    rgb_to_bgr,
    bgr_to_grayscale,
    draw_bounding_box,
    draw_text,
    crop_roi,
    frame_to_jpeg_bytes,
    frame_to_base64,
    base64_to_frame,
    save_frame_to_file,
    apply_gaussian_blur,
    enhance_contrast,
    histogram_equalization,
    get_frame_dimensions,
    get_frame_brightness,
)

__all__ = [
    # Constants
    "CameraEventType",
    "DetectorType",
    "SensorType",
    "DeviceStatus",
    "AlertSeverity",
    "AlertCategory",
    "ShelfStockStatus",
    "ModelConfig",
    "SensorThresholds",
    "CameraConfig",
    "CommunicationConfig",
    "LogConfig",
    # Logger
    "EdgeAILogger",
    "logger",
    "log_debug",
    "log_info",
    "log_warning",
    "log_error",
    "log_critical",
    "log_exception",
    # Helpers
    "generate_event_id",
    "generate_device_id",
    "generate_frame_id",
    "get_utc_timestamp",
    "get_utc_timestamp_ms",
    "timestamp_to_iso",
    "parse_iso_timestamp",
    "distance_euclidean",
    "bounding_box_area",
    "bounding_box_center",
    "normalize_confidence",
    "percentage",
    "to_json_serializable",
    "dict_to_json",
    "json_to_dict",
    "ensure_directory",
    "save_json_file",
    "load_json_file",
    "is_valid_bbox",
    "is_valid_confidence",
    "clamp",
    # Image utilities
    "resize_frame",
    "normalize_frame",
    "bgr_to_rgb",
    "rgb_to_bgr",
    "bgr_to_grayscale",
    "draw_bounding_box",
    "draw_text",
    "crop_roi",
    "frame_to_jpeg_bytes",
    "frame_to_base64",
    "base64_to_frame",
    "save_frame_to_file",
    "apply_gaussian_blur",
    "enhance_contrast",
    "histogram_equalization",
    "get_frame_dimensions",
    "get_frame_brightness",
]
