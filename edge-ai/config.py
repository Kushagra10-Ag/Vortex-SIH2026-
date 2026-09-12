"""
Edge-AI Configuration Module
Loads configuration from environment variables or defaults
Centralized settings for backend communication, devices, models, and sensors
"""

import os
from dotenv import load_dotenv

# Load .env file from edge-ai directory
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)


class EdgeAIConfig:
    """Configuration for edge-ai application"""
    
    # ════════════════════════════════════════════════════════════════════════════
    # BACKEND API CONFIGURATION
    # ════════════════════════════════════════════════════════════════════════════
    
    BACKEND_API_URL = os.getenv('BACKEND_API_URL', 'http://127.0.0.1:5000')
    """Backend Flask API base URL for sending data"""
    
    BACKEND_API_KEY = os.getenv('BACKEND_API_KEY', '')
    """Optional API key for backend authentication"""
    
    # ════════════════════════════════════════════════════════════════════════════
    # DEVICE IDENTIFICATION
    # ════════════════════════════════════════════════════════════════════════════
    
    DEVICE_ID = os.getenv('DEVICE_ID', 'edge-ai-device-001')
    """Unique identifier for this edge device"""
    
    DEVICE_NAME = os.getenv('DEVICE_NAME', 'Edge AI Box')
    """Human-readable name for this device"""
    
    DEVICE_TYPE = os.getenv('DEVICE_TYPE', 'edge_ai_box')
    """Type of device (edge_ai_box, camera, sensor_hub)"""
    
    DEVICE_LOCATION = os.getenv('DEVICE_LOCATION', 'Store Floor')
    """Physical location of this device"""
    
    IP_ADDRESS = os.getenv('IP_ADDRESS', '')
    """IP address of edge device (auto-detected if empty)"""
    
    MAC_ADDRESS = os.getenv('MAC_ADDRESS', '')
    """MAC address of edge device (auto-detected if empty)"""
    
    FIRMWARE_VERSION = os.getenv('FIRMWARE_VERSION', '1.0.0')
    """Firmware version of this device"""
    
    # ════════════════════════════════════════════════════════════════════════════
    # CAMERA CONFIGURATION
    # ════════════════════════════════════════════════════════════════════════════
    
    CAMERA_SOURCE = os.getenv('CAMERA_SOURCE', '0')
    """
    Camera source:
    - '0' for default USB camera
    - integer for webcam index (1, 2, etc.)
    - RTSP URL like 'rtsp://192.168.1.100:554/stream'
    - Path to video file for testing
    """
    
    CAMERA_FPS = int(os.getenv('CAMERA_FPS', '30'))
    """Target frames per second for camera capture"""
    
    CAMERA_WIDTH = int(os.getenv('CAMERA_WIDTH', '1280'))
    """Camera resolution width"""
    
    CAMERA_HEIGHT = int(os.getenv('CAMERA_HEIGHT', '720'))
    """Camera resolution height"""
    
    CAMERA_WARMUP_FRAMES = int(os.getenv('CAMERA_WARMUP_FRAMES', '30'))
    """Number of frames to skip after camera start (for stabilization)"""
    
    ENABLE_FRAME_PREVIEW = os.getenv('ENABLE_FRAME_PREVIEW', 'false').lower() == 'true'
    """Enable OpenCV window preview (disable on headless servers)"""
    
    # ════════════════════════════════════════════════════════════════════════════
    # AI MODEL CONFIGURATION
    # ════════════════════════════════════════════════════════════════════════════
    
    YOLO_MODEL_NAME = os.getenv('YOLO_MODEL_NAME', 'yolo11n.pt')
    """
    Ultralytics pretrained name used when local weights are missing or empty.
    Default is YOLOv11 nano (edge-friendly). Alternatives: yolo11s.pt, yolov8n.pt.
    """

    YOLO_WEIGHTS_PATH = os.getenv('YOLO_WEIGHTS_PATH', 'weights/yolov11.pt')
    """Local .pt path (relative to edge-ai/ or absolute). Cached after first download."""
    
    MODEL_CONFIDENCE_THRESHOLD = float(os.getenv('MODEL_CONFIDENCE_THRESHOLD', '0.5'))
    """Minimum confidence score for detections"""
    
    MODEL_IOU_THRESHOLD = float(os.getenv('MODEL_IOU_THRESHOLD', '0.45'))
    """NMS (Non-Maximum Suppression) IOU threshold"""
    
    INFERENCE_SKIP_FRAMES = int(os.getenv('INFERENCE_SKIP_FRAMES', '3'))
    """Run inference every N frames (skip frames for performance)"""
    
    ENABLE_GPU = os.getenv('ENABLE_GPU', 'false').lower() == 'true'
    """Use GPU for model inference (CUDA/cuDNN required)"""
    
    # ════════════════════════════════════════════════════════════════════════════
    # SENSOR CONFIGURATION
    # ════════════════════════════════════════════════════════════════════════════
    
    ENABLE_DHT22 = os.getenv('ENABLE_DHT22', 'false').lower() == 'true'
    """Enable DHT22 temperature/humidity sensor"""
    
    DHT22_PIN = int(os.getenv('DHT22_PIN', '17'))
    """GPIO pin number for DHT22 sensor"""
    
    ENABLE_HX711 = os.getenv('ENABLE_HX711', 'false').lower() == 'true'
    """Enable HX711 load cell (shelf weight) sensor"""
    
    HX711_DATA_PIN = int(os.getenv('HX711_DATA_PIN', '5'))
    """GPIO pin for HX711 DATA line"""
    
    HX711_CLOCK_PIN = int(os.getenv('HX711_CLOCK_PIN', '6'))
    """GPIO pin for HX711 CLOCK line"""
    
    ENABLE_PIR = os.getenv('ENABLE_PIR', 'false').lower() == 'true'
    """Enable PIR motion detection sensor"""
    
    PIR_PIN = int(os.getenv('PIR_PIN', '27'))
    """GPIO pin for PIR sensor"""
    
    ENABLE_ULTRASONIC = os.getenv('ENABLE_ULTRASONIC', 'false').lower() == 'true'
    """Enable ultrasonic distance sensor"""
    
    ULTRASONIC_TRIG_PIN = int(os.getenv('ULTRASONIC_TRIG_PIN', '23'))
    """GPIO pin for ultrasonic TRIG (trigger)"""
    
    ULTRASONIC_ECHO_PIN = int(os.getenv('ULTRASONIC_ECHO_PIN', '24'))
    """GPIO pin for ultrasonic ECHO (receive)"""
    
    USE_MOCK_SENSORS = os.getenv('USE_MOCK_SENSORS', 'true').lower() == 'true'
    """Use simulated sensor data for testing (when actual hardware unavailable)"""
    
    SENSOR_READ_INTERVAL_SECONDS = int(os.getenv('SENSOR_READ_INTERVAL_SECONDS', '30'))
    """How often to read and send sensor readings"""
    
    # ════════════════════════════════════════════════════════════════════════════
    # COMMUNICATION CONFIGURATION
    # ════════════════════════════════════════════════════════════════════════════
    
    HEARTBEAT_INTERVAL_SECONDS = int(os.getenv('HEARTBEAT_INTERVAL_SECONDS', '60'))
    """How often to send heartbeat to backend"""
    
    REQUEST_TIMEOUT_SECONDS = int(os.getenv('REQUEST_TIMEOUT_SECONDS', '10'))
    """Timeout for HTTP requests to backend"""
    
    RECONNECT_RETRY_ATTEMPTS = int(os.getenv('RECONNECT_RETRY_ATTEMPTS', '3'))
    """Number of retry attempts for failed requests"""
    
    RECONNECT_BACKOFF_SECONDS = int(os.getenv('RECONNECT_BACKOFF_SECONDS', '5'))
    """Backoff time between retry attempts"""
    
    EVENT_BATCH_SIZE = int(os.getenv('EVENT_BATCH_SIZE', '10'))
    """Number of events to batch before sending"""
    
    EVENT_FLUSH_INTERVAL_SECONDS = int(os.getenv('EVENT_FLUSH_INTERVAL_SECONDS', '5'))
    """Flush buffered events after this time even if batch size not reached"""
    
    # ════════════════════════════════════════════════════════════════════════════
    # LOGGING & DEBUG
    # ════════════════════════════════════════════════════════════════════════════
    
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    """Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL"""
    
    LOG_FILE = os.getenv('LOG_FILE', 'logs/edge_ai.log')
    """Path to log file"""
    
    DEBUG_MODE = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
    """Enable debug mode (verbose logging, frame preview)"""
    
    SAVE_DETECTION_SNAPSHOTS = os.getenv('SAVE_DETECTION_SNAPSHOTS', 'false').lower() == 'true'
    """Save snapshots of detections to disk for debugging"""
    
    SNAPSHOT_DIR = os.getenv('SNAPSHOT_DIR', 'snapshots/')
    """Directory to save detection snapshots"""
    
    # ════════════════════════════════════════════════════════════════════════════
    # DETECTION THRESHOLDS & RULES
    # ════════════════════════════════════════════════════════════════════════════
    
    PERSON_COUNT_WARNING = int(os.getenv('PERSON_COUNT_WARNING', '5'))
    """Alert if person count exceeds this"""
    
    QUEUE_LENGTH_THRESHOLD = int(os.getenv('QUEUE_LENGTH_THRESHOLD', '3'))
    """Trigger queue alert if people count >= this"""
    
    DWELL_TIME_WARNING_SECONDS = int(os.getenv('DWELL_TIME_WARNING_SECONDS', '30'))
    """Alert if person stays in frame for this long (dwell time)"""
    
    # ════════════════════════════════════════════════════════════════════════════
    # OPTIONAL: GOOGLE GEMINI API (for LLM-based alerts)
    # ════════════════════════════════════════════════════════════════════════════
    
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    """Google Generative AI API key (for optional LLM-based insights)"""
    
    # ════════════════════════════════════════════════════════════════════════════
    # CLASS METHODS FOR VALIDATION & PRETTY-PRINTING
    # ════════════════════════════════════════════════════════════════════════════
    
    @classmethod
    def to_dict(cls) -> dict:
        """Export configuration as dictionary"""
        return {
            'backend_api_url': cls.BACKEND_API_URL,
            'device_id': cls.DEVICE_ID,
            'device_name': cls.DEVICE_NAME,
            'device_type': cls.DEVICE_TYPE,
            'camera_source': cls.CAMERA_SOURCE,
            'camera_fps': cls.CAMERA_FPS,
            'camera_resolution': f"{cls.CAMERA_WIDTH}x{cls.CAMERA_HEIGHT}",
            'yolo_model': cls.YOLO_MODEL_NAME,
            'yolo_weights_path': cls.YOLO_WEIGHTS_PATH,
            'inference_skip_frames': cls.INFERENCE_SKIP_FRAMES,
            'sensors': {
                'use_mock': cls.USE_MOCK_SENSORS,
                'dht22': cls.ENABLE_DHT22,
                'hx711': cls.ENABLE_HX711,
                'pir': cls.ENABLE_PIR,
                'ultrasonic': cls.ENABLE_ULTRASONIC,
            },
            'heartbeat_interval': cls.HEARTBEAT_INTERVAL_SECONDS,
            'log_level': cls.LOG_LEVEL,
            'debug_mode': cls.DEBUG_MODE,
        }
    
    @classmethod
    def validate(cls) -> tuple:
        """
        Validate critical configuration values
        
        Returns:
            tuple: (is_valid: bool, errors: list[str])
        """
        errors = []
        
        if not cls.BACKEND_API_URL:
            errors.append("BACKEND_API_URL not set")
        
        if not cls.DEVICE_ID:
            errors.append("DEVICE_ID not set")
        
        if cls.CAMERA_FPS <= 0 or cls.CAMERA_FPS > 120:
            errors.append(f"CAMERA_FPS must be 1-120, got {cls.CAMERA_FPS}")
        
        if cls.CAMERA_WIDTH <= 0 or cls.CAMERA_HEIGHT <= 0:
            errors.append(f"Invalid camera resolution: {cls.CAMERA_WIDTH}x{cls.CAMERA_HEIGHT}")
        
        if cls.MODEL_CONFIDENCE_THRESHOLD < 0 or cls.MODEL_CONFIDENCE_THRESHOLD > 1:
            errors.append(f"MODEL_CONFIDENCE_THRESHOLD must be 0-1, got {cls.MODEL_CONFIDENCE_THRESHOLD}")
        
        return (len(errors) == 0, errors)


# Export config as singleton
config = EdgeAIConfig()
