"""
Constants, Enums, and Configuration Values for Edge-AI Module
Shared across vision detection, sensor processing, and event system
"""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EVENT TYPES — Camera Vision Events
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class CameraEventType:
    """Vision AI detection events"""
    PERSON_DETECTED = "person_detected"
    SHELF_GRAB = "shelf_grab"
    QUEUE_OVERFLOW = "queue_overflow"
    OUT_OF_STOCK_DETECTED = "out_of_stock_detected"
    THEFT_ALERT = "theft_alert"
    DWELL_TIME_HIGH = "dwell_time_high"
    MISPLACED_ITEM = "misplaced_item"
    QUEUE_EMPTY = "queue_empty"
    UNUSUAL_ACTIVITY = "unusual_activity"

    ALL = [
        PERSON_DETECTED,
        SHELF_GRAB,
        QUEUE_OVERFLOW,
        OUT_OF_STOCK_DETECTED,
        THEFT_ALERT,
        DWELL_TIME_HIGH,
        MISPLACED_ITEM,
        QUEUE_EMPTY,
        UNUSUAL_ACTIVITY,
    ]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DETECTOR TYPES — AI Model Types
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class DetectorType:
    """Available AI detectors on edge device"""
    PERSON_DETECTOR = "person_detector"
    QUEUE_DETECTOR = "queue_detector"
    SHELF_DETECTOR = "shelf_detector"
    TRACKER = "tracker"

    ALL = [PERSON_DETECTOR, QUEUE_DETECTOR, SHELF_DETECTOR, TRACKER]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SENSOR TYPES — IoT Sensor Data
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class SensorType:
    """IoT sensor types supported by edge device"""
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    WEIGHT = "weight"
    IR_DISTANCE = "ir_distance"
    ULTRASONIC_DISTANCE = "ultrasonic_distance"
    MOTION_PIR = "motion_pir"
    AMBIENT_LIGHT = "ambient_light"

    ALL = [TEMPERATURE, HUMIDITY, WEIGHT, IR_DISTANCE, ULTRASONIC_DISTANCE, MOTION_PIR, AMBIENT_LIGHT]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DEVICE STATUS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class DeviceStatus:
    """Edge device status values"""
    ONLINE = "online"
    OFFLINE = "offline"
    WARNING = "warning"
    MAINTENANCE = "maintenance"

    ALL = [ONLINE, OFFLINE, WARNING, MAINTENANCE]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ALERT SEVERITY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class AlertSeverity:
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

    ALL = [INFO, WARNING, CRITICAL]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ALERT CATEGORIES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class AlertCategory:
    """Alert category for system event routing"""
    SHELF_STOCK = "shelf_stock"
    THEFT_SECURITY = "theft_security"
    SENSOR_ANOMALY = "sensor_anomaly"
    DEVICE_OFFLINE = "device_offline"
    EXPIRY_WARNING = "expiry_warning"
    FOOTFALL_SURGE = "footfall_surge"
    SYSTEM = "system"

    ALL = [
        SHELF_STOCK,
        THEFT_SECURITY,
        SENSOR_ANOMALY,
        DEVICE_OFFLINE,
        EXPIRY_WARNING,
        FOOTFALL_SURGE,
        SYSTEM,
    ]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SHELF STOCK STATUS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class ShelfStockStatus:
    """Shelf fill status"""
    NORMAL = "normal"
    LOW_STOCK = "low_stock"
    EMPTY = "empty"
    MISPLACED_ITEM = "misplaced_item"

    ALL = [NORMAL, LOW_STOCK, EMPTY, MISPLACED_ITEM]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MODEL CONFIGURATION & THRESHOLDS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class ModelConfig:
    """YOLO and AI model configuration"""
    
    # YOLO Model Selection
    YOLO_MODEL = "yolov5s"  # Options: yolov5s, yolov5m, yolov5l, yolov8s, yolov8m
    
    # Detection Confidence Thresholds
    PERSON_CONFIDENCE_THRESHOLD = 0.5
    SHELF_CONFIDENCE_THRESHOLD = 0.6
    QUEUE_CONFIDENCE_THRESHOLD = 0.55
    
    # Tracking
    TRACKER_MAX_AGE = 30  # frames
    TRACKER_MIN_HITS = 3  # minimum detections before confirming track
    
    # Queue Detection
    QUEUE_THRESHOLD = 3  # people count to trigger queue alert
    QUEUE_ALERT_THRESHOLD = 5  # critical queue length
    
    # Dwell Time
    DWELL_TIME_WARNING_SECONDS = 30
    DWELL_TIME_CRITICAL_SECONDS = 60
    
    # Shelf Analysis
    SHELF_LOW_STOCK_PERCENTAGE = 30  # fill percentage below this is "low"
    SHELF_EMPTY_PERCENTAGE = 10  # fill percentage below this is "empty"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SENSOR THRESHOLDS (Default Values)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class SensorThresholds:
    """Default sensor anomaly detection thresholds"""
    
    # Temperature (°C) — Cooler/Freezer Section
    TEMPERATURE_FREEZER_MIN = -20.0
    TEMPERATURE_FREEZER_MAX = -10.0
    TEMPERATURE_COOLER_MIN = 2.0
    TEMPERATURE_COOLER_MAX = 8.0
    TEMPERATURE_AMBIENT_MIN = 15.0
    TEMPERATURE_AMBIENT_MAX = 28.0
    
    # Humidity (%)
    HUMIDITY_MIN = 30.0
    HUMIDITY_MAX = 70.0
    
    # Weight (kg) — Shelf Load Cell
    WEIGHT_MIN = 0.0
    WEIGHT_MAX = 50.0
    
    # Distance (cm) — IR or Ultrasonic
    DISTANCE_MIN = 5.0
    DISTANCE_MAX = 300.0


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CAMERA & FRAME PROCESSING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class CameraConfig:
    """Camera and frame processing settings"""
    
    # Frame Capture
    FRAME_WIDTH = 1280
    FRAME_HEIGHT = 720
    FRAME_FPS = 30
    
    # Processing
    INFERENCE_FPS = 10  # Run AI inference every N frames (skip frames for performance)
    FRAME_QUALITY_JPEG = 80  # JPEG compression quality for snapshots sent to backend
    
    # Model Input
    MODEL_INPUT_SIZE = 640  # YOLO input size


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# COMMUNICATION & TIMING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class CommunicationConfig:
    """Backend API and communication settings"""
    
    # Heartbeat (keep-alive)
    HEARTBEAT_INTERVAL_SECONDS = 60
    
    # Sensor Readings
    SENSOR_READING_INTERVAL_SECONDS = 30
    
    # Camera Events
    CAMERA_EVENT_BATCH_SIZE = 10  # batch events before sending
    CAMERA_EVENT_FLUSH_INTERVAL_SECONDS = 5  # send buffered events after this time
    
    # Network
    REQUEST_TIMEOUT_SECONDS = 10
    RECONNECT_RETRY_ATTEMPTS = 3
    RECONNECT_BACKOFF_SECONDS = 5


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LOGGING & DEBUG
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class LogConfig:
    """Logging configuration"""
    
    LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_FILE = "logs/edge_ai.log"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_RETENTION_DAYS = 7
