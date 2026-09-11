"""
Event Builder — Factory Methods for All Edge-AI Events
Constructs structured event objects from raw detection/sensor data.

Usage:
    builder = EventBuilder(device_id="edge-001")
    event = builder.person_detected(count=3, bbox=[100, 50, 80, 200], confidence=0.91)
"""

import time
from typing import Optional, List, Dict, Any

from .event_types import (
    CameraEvent,
    SensorEvent,
    FootfallEvent,
    HeartbeatEvent,
    Detection,
)
from ..utils.constants import CameraEventType, SensorType
from ..utils.helpers import generate_event_id, get_utc_timestamp
from ..utils.image_utils import frame_to_base64

try:
    import numpy as np
    _HAS_NUMPY = True
except ImportError:
    _HAS_NUMPY = False


class EventBuilder:
    """
    Factory class for constructing all edge-ai event types.

    Args:
        device_id: The backend-registered device ID for this edge node.
        capture_snapshots: If True, attach base64 JPEG snapshots to camera events.
    """

    def __init__(self, device_id: str, capture_snapshots: bool = False):
        self.device_id = device_id
        self.capture_snapshots = capture_snapshots

    # ─────────────────────────────────────────────────────────────────────────
    # CAMERA EVENTS
    # ─────────────────────────────────────────────────────────────────────────

    def person_detected(
        self,
        count: int,
        bbox: Optional[List[int]] = None,
        confidence: float = 1.0,
        frame=None,
    ) -> CameraEvent:
        """
        Build PERSON_DETECTED event.

        Args:
            count:      Number of persons detected in this frame.
            bbox:       Bounding box [x, y, w, h] of the primary/largest person.
            confidence: Detection confidence score.
            frame:      Raw numpy frame (used for snapshot if enabled).

        Returns:
            CameraEvent with event_type='person_detected'
        """
        return CameraEvent(
            event_type=CameraEventType.PERSON_DETECTED,
            device_id=self.device_id,
            confidence=round(confidence, 4),
            bounding_box=bbox,
            person_count=count,
            frame_base64=self._maybe_snapshot(frame),
            metadata={"person_count": count},
        )

    def queue_overflow(
        self,
        count: int,
        bbox: Optional[List[int]] = None,
        confidence: float = 1.0,
        frame=None,
    ) -> CameraEvent:
        """
        Build QUEUE_OVERFLOW event when person count exceeds threshold.

        Args:
            count:      Number of persons in queue zone.
            bbox:       Bounding box of the queue area.
            confidence: Confidence of detection.
            frame:      Raw numpy frame for snapshot.

        Returns:
            CameraEvent with event_type='queue_overflow'
        """
        return CameraEvent(
            event_type=CameraEventType.QUEUE_OVERFLOW,
            device_id=self.device_id,
            confidence=round(confidence, 4),
            bounding_box=bbox,
            person_count=count,
            frame_base64=self._maybe_snapshot(frame),
            metadata={"queue_length": count},
        )

    def queue_empty(self, frame=None) -> CameraEvent:
        """
        Build QUEUE_EMPTY event when queue clears.

        Returns:
            CameraEvent with event_type='queue_empty'
        """
        return CameraEvent(
            event_type=CameraEventType.QUEUE_EMPTY,
            device_id=self.device_id,
            confidence=1.0,
            person_count=0,
            frame_base64=self._maybe_snapshot(frame),
            metadata={"queue_length": 0},
        )

    def theft_alert(
        self,
        bbox: Optional[List[int]] = None,
        confidence: float = 0.8,
        frame=None,
        zone_id: Optional[str] = None,
    ) -> CameraEvent:
        """
        Build THEFT_ALERT event for suspicious shelf activity.

        Args:
            bbox:       Region where suspicious activity was detected.
            confidence: Confidence of the theft signal.
            frame:      Frame snapshot (always captured for theft alerts).
            zone_id:    Shelf zone identifier.

        Returns:
            CameraEvent with event_type='theft_alert'
        """
        # For security events, always try to capture snapshot
        snapshot = None
        if frame is not None and _HAS_NUMPY:
            snapshot = frame_to_base64(frame, quality=85)

        return CameraEvent(
            event_type=CameraEventType.THEFT_ALERT,
            device_id=self.device_id,
            confidence=round(confidence, 4),
            bounding_box=bbox,
            frame_base64=snapshot,
            metadata={"zone_id": zone_id} if zone_id else {},
        )

    def out_of_stock(
        self,
        fill_percentage: float,
        shelf_zone_id: Optional[str] = None,
        frame=None,
    ) -> CameraEvent:
        """
        Build OUT_OF_STOCK_DETECTED event when shelf fill % is below threshold.

        Args:
            fill_percentage: Estimated fill % of the shelf (0–100).
            shelf_zone_id:   Shelf zone label (e.g. 'A1', 'B2').
            frame:           Frame snapshot.

        Returns:
            CameraEvent with event_type='out_of_stock_detected'
        """
        return CameraEvent(
            event_type=CameraEventType.OUT_OF_STOCK_DETECTED,
            device_id=self.device_id,
            confidence=round(max(0.0, (100 - fill_percentage) / 100), 4),
            frame_base64=self._maybe_snapshot(frame),
            metadata={
                "fill_percentage": round(fill_percentage, 2),
                "shelf_zone": shelf_zone_id or "unknown",
            },
        )

    def dwell_time_high(
        self,
        track_id: int,
        dwell_seconds: float,
        bbox: Optional[List[int]] = None,
        frame=None,
    ) -> CameraEvent:
        """
        Build DWELL_TIME_HIGH event when a person stays too long in frame.

        Args:
            track_id:      Persistent track ID of the person.
            dwell_seconds: How many seconds the person has been in frame.
            bbox:          Current bounding box of the person.
            frame:         Frame snapshot.

        Returns:
            CameraEvent with event_type='dwell_time_high'
        """
        return CameraEvent(
            event_type=CameraEventType.DWELL_TIME_HIGH,
            device_id=self.device_id,
            confidence=0.9,
            bounding_box=bbox,
            frame_base64=self._maybe_snapshot(frame),
            metadata={
                "track_id": track_id,
                "dwell_seconds": round(dwell_seconds, 1),
            },
        )

    # ─────────────────────────────────────────────────────────────────────────
    # SENSOR EVENTS
    # ─────────────────────────────────────────────────────────────────────────

    def sensor_reading(
        self,
        sensor_type: str,
        value: float,
        unit: str,
        is_anomaly: bool = False,
        threshold_min: Optional[float] = None,
        threshold_max: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SensorEvent:
        """
        Build a generic sensor reading event.

        Args:
            sensor_type:    Type string (e.g. 'temperature', 'humidity', 'weight')
            value:          Numeric reading value
            unit:           Unit of measurement (e.g. '°C', '%', 'kg')
            is_anomaly:     True if value exceeds thresholds
            threshold_min:  Minimum threshold
            threshold_max:  Maximum threshold
            metadata:       Extra context dict

        Returns:
            SensorEvent
        """
        return SensorEvent(
            device_id=self.device_id,
            sensor_type=sensor_type,
            value=round(value, 4),
            unit=unit,
            is_anomaly=is_anomaly,
            threshold_min=threshold_min,
            threshold_max=threshold_max,
            metadata=metadata or {},
        )

    def temperature_reading(
        self,
        celsius: float,
        is_anomaly: bool = False,
        threshold_min: float = 2.0,
        threshold_max: float = 28.0,
    ) -> SensorEvent:
        """Build temperature sensor reading event."""
        return self.sensor_reading(
            sensor_type=SensorType.TEMPERATURE,
            value=celsius,
            unit="°C",
            is_anomaly=is_anomaly,
            threshold_min=threshold_min,
            threshold_max=threshold_max,
        )

    def humidity_reading(
        self,
        percent: float,
        is_anomaly: bool = False,
        threshold_min: float = 30.0,
        threshold_max: float = 70.0,
    ) -> SensorEvent:
        """Build humidity sensor reading event."""
        return self.sensor_reading(
            sensor_type=SensorType.HUMIDITY,
            value=percent,
            unit="%",
            is_anomaly=is_anomaly,
            threshold_min=threshold_min,
            threshold_max=threshold_max,
        )

    def weight_reading(
        self,
        kg: float,
        shelf_id: Optional[str] = None,
        is_anomaly: bool = False,
    ) -> SensorEvent:
        """Build shelf weight (load cell) reading event."""
        return self.sensor_reading(
            sensor_type=SensorType.WEIGHT,
            value=kg,
            unit="kg",
            is_anomaly=is_anomaly,
            metadata={"shelf_id": shelf_id} if shelf_id else {},
        )

    def distance_reading(
        self,
        cm: float,
        sensor_type: str = SensorType.IR_DISTANCE,
        is_anomaly: bool = False,
    ) -> SensorEvent:
        """Build distance sensor (IR / ultrasonic) reading event."""
        return self.sensor_reading(
            sensor_type=sensor_type,
            value=cm,
            unit="cm",
            is_anomaly=is_anomaly,
        )

    # ─────────────────────────────────────────────────────────────────────────
    # FOOTFALL EVENTS
    # ─────────────────────────────────────────────────────────────────────────

    def footfall(
        self,
        entry_count: int,
        exit_count: int,
        current_occupancy: int,
        dwell_time_avg: float = 0.0,
    ) -> FootfallEvent:
        """
        Build a footfall (visitor count) event.

        Args:
            entry_count:        New entries this interval.
            exit_count:         New exits this interval.
            current_occupancy:  Current live occupancy.
            dwell_time_avg:     Average dwell time in seconds.

        Returns:
            FootfallEvent
        """
        return FootfallEvent(
            device_id=self.device_id,
            entry_count=entry_count,
            exit_count=exit_count,
            current_occupancy=max(0, current_occupancy),
            dwell_time_avg=dwell_time_avg,
        )

    # ─────────────────────────────────────────────────────────────────────────
    # HEARTBEAT EVENTS
    # ─────────────────────────────────────────────────────────────────────────

    def heartbeat(
        self,
        status: str = "online",
        uptime_seconds: float = 0.0,
        firmware_version: str = "1.0.0",
    ) -> HeartbeatEvent:
        """
        Build a device heartbeat event.

        Args:
            status:             Device status string ('online', 'warning')
            uptime_seconds:     Seconds since daemon started
            firmware_version:   Firmware version string

        Returns:
            HeartbeatEvent
        """
        # Try to get real CPU/memory stats
        cpu_pct = 0.0
        mem_pct = 0.0
        try:
            import psutil
            cpu_pct = psutil.cpu_percent(interval=None)
            mem_pct = psutil.virtual_memory().percent
        except ImportError:
            pass  # psutil optional; zero values are fine

        return HeartbeatEvent(
            device_id=self.device_id,
            status=status,
            firmware_version=firmware_version,
            uptime_seconds=uptime_seconds,
            cpu_percent=cpu_pct,
            memory_percent=mem_pct,
        )

    # ─────────────────────────────────────────────────────────────────────────
    # INTERNAL HELPERS
    # ─────────────────────────────────────────────────────────────────────────

    def _maybe_snapshot(self, frame) -> Optional[str]:
        """
        Return base64-encoded JPEG snapshot if snapshot capture is enabled
        and frame is valid.

        Args:
            frame: NumPy ndarray frame, or None.

        Returns:
            Base64 string or None.
        """
        if not self.capture_snapshots or frame is None:
            return None
        if not _HAS_NUMPY:
            return None
        try:
            return frame_to_base64(frame, quality=75)
        except Exception:
            return None

