"""
Event Type Definitions for Edge-AI Module
Dataclasses representing structured events sent to the BIZmate backend.

Three primary event types:
  - CameraEvent  → /monitoring/camera-events
  - SensorEvent  → /sensors/readings
  - FootfallEvent → /monitoring/footfall
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone


def _utc_now_iso() -> str:
    """Return current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DETECTION — bounding box, confidence
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass
class Detection:
    """
    Single object detection result from YOLO inference.

    Attributes:
        class_id:    COCO class integer (0 = person, 39 = bottle, etc.)
        class_name:  Human-readable class label (e.g. 'person')
        confidence:  Detection confidence score [0.0 – 1.0]
        bbox:        [x, y, width, height] in pixels (top-left origin)
        center:      (cx, cy) center of bounding box in pixels
        track_id:    Optional persistent tracker ID across frames
    """
    class_id: int
    class_name: str
    confidence: float
    bbox: List[int]                    # [x, y, w, h]
    center: tuple = field(default=(0, 0))
    track_id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "class_id": self.class_id,
            "class_name": self.class_name,
            "confidence": round(self.confidence, 4),
            "bbox": self.bbox,
            "center": list(self.center),
            "track_id": self.track_id,
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CAMERA EVENT → POST /monitoring/camera-events
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass
class CameraEvent:
    """
    Vision-AI detection event posted to /monitoring/camera-events.

    Attributes:
        event_type:     Type string matching CameraEventType constants
                        e.g. 'person_detected', 'queue_overflow', 'theft_alert'
        device_id:      Backend device ID for the camera/edge-ai-box
        confidence:     Overall event confidence [0.0 – 1.0]
        bounding_box:   Primary bounding box [x, y, w, h] (most relevant detection)
        timestamp:      UTC ISO timestamp of the detection
        person_count:   Number of persons in frame at time of event
        frame_base64:   Optional JPEG snapshot encoded as base64 string
        metadata:       Free-form extra data dict (dwell_seconds, zone_id, etc.)
    """
    event_type: str
    device_id: str
    confidence: float
    bounding_box: Optional[List[int]] = None
    timestamp: str = field(default_factory=_utc_now_iso)
    person_count: int = 0
    frame_base64: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict compatible with /monitoring/camera-events payload."""
        return {
            "event_type": self.event_type,
            "device_id": self.device_id,
            "confidence": round(self.confidence, 4),
            "bounding_box": self.bounding_box,
            "timestamp": self.timestamp,
            "person_count": self.person_count,
            "frame_snapshot": self.frame_base64,
            "metadata": self.metadata,
        }

    def to_backend_payload(self) -> Dict[str, Any]:
        """
        Format payload exactly as expected by backend MonitoringService.

        Maps to:
            CameraEvent model fields in backend/app/models/camera_event.py
        """
        payload = self.to_dict()
        # Remove None values — backend validates required fields server-side
        return {k: v for k, v in payload.items() if v is not None}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SENSOR EVENT → POST /sensors/readings
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass
class SensorEvent:
    """
    IoT sensor reading posted to /sensors/readings.

    Attributes:
        device_id:      Backend device ID for the sensor hub / edge box
        sensor_type:    Type string matching SensorType constants
                        e.g. 'temperature', 'humidity', 'weight'
        value:          Numeric sensor reading
        unit:           Unit string (e.g. '°C', '%', 'kg', 'cm')
        is_anomaly:     True if reading exceeds configured thresholds
        threshold_min:  Minimum acceptable value (from SensorThresholds)
        threshold_max:  Maximum acceptable value (from SensorThresholds)
        timestamp:      UTC ISO timestamp
        metadata:       Extra context (gpio_pin, location, etc.)
    """
    device_id: str
    sensor_type: str
    value: float
    unit: str
    is_anomaly: bool = False
    threshold_min: Optional[float] = None
    threshold_max: Optional[float] = None
    timestamp: str = field(default_factory=_utc_now_iso)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "device_id": self.device_id,
            "sensor_type": self.sensor_type,
            "value": self.value,
            "unit": self.unit,
            "is_anomaly": self.is_anomaly,
            "threshold_min": self.threshold_min,
            "threshold_max": self.threshold_max,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }

    def to_backend_payload(self) -> Dict[str, Any]:
        """Format payload for /sensors/readings endpoint."""
        payload = self.to_dict()
        return {k: v for k, v in payload.items() if v is not None}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FOOTFALL EVENT → POST /monitoring/footfall
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass
class FootfallEvent:
    """
    Visitor traffic event posted to /monitoring/footfall.

    Attributes:
        device_id:          Backend device ID (footfall_counter / camera)
        entry_count:        Number of new entries detected this interval
        exit_count:         Number of exits detected this interval
        current_occupancy:  Current live count in store (cumulative)
        dwell_time_avg:     Average time (seconds) persons spent in frame
        timestamp:          UTC ISO timestamp
    """
    device_id: str
    entry_count: int
    exit_count: int
    current_occupancy: int
    dwell_time_avg: float = 0.0
    timestamp: str = field(default_factory=_utc_now_iso)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "device_id": self.device_id,
            "entry_count": self.entry_count,
            "exit_count": self.exit_count,
            "current_occupancy": self.current_occupancy,
            "dwell_time_avg": round(self.dwell_time_avg, 2),
            "timestamp": self.timestamp,
        }

    def to_backend_payload(self) -> Dict[str, Any]:
        """Format payload for /monitoring/footfall endpoint."""
        return self.to_dict()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HEARTBEAT EVENT → POST /devices/heartbeat
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass
class HeartbeatEvent:
    """
    Device keepalive ping posted to /devices/heartbeat.

    Attributes:
        device_id:          Backend device ID
        status:             Current device status ('online', 'warning')
        firmware_version:   Running firmware version string
        uptime_seconds:     Seconds since daemon started
        cpu_percent:        CPU usage percentage (0–100)
        memory_percent:     Memory usage percentage (0–100)
        timestamp:          UTC ISO timestamp
    """
    device_id: str
    status: str = "online"
    firmware_version: str = "1.0.0"
    uptime_seconds: float = 0.0
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    timestamp: str = field(default_factory=_utc_now_iso)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "device_id": self.device_id,
            "status": self.status,
            "firmware_version": self.firmware_version,
            "uptime_seconds": round(self.uptime_seconds, 1),
            "cpu_percent": round(self.cpu_percent, 1),
            "memory_percent": round(self.memory_percent, 1),
            "timestamp": self.timestamp,
        }

    def to_backend_payload(self) -> Dict[str, Any]:
        return self.to_dict()

