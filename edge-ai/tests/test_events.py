"""
Event Tests
Test event building, event types, and payload formatting for backend compatibility.
"""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from events.event_types import CameraEvent, SensorEvent, FootfallEvent, HeartbeatEvent, Detection
from events.event_builder import EventBuilder
from utils.constants import CameraEventType, SensorType


class TestCameraEvent:
    """Test camera event data structure and payload formatting."""

    def test_camera_event_creation(self):
        """Test basic camera event creation."""
        event = CameraEvent(
            event_type="person_detected",
            device_id="edge-001",
            confidence=0.95,
            bounding_box=[100, 200, 50, 100],
            person_count=3
        )

        assert event.event_type == "person_detected"
        assert event.device_id == "edge-001"
        assert event.confidence == 0.95
        assert event.bounding_box == [100, 200, 50, 100]
        assert event.person_count == 3

    def test_camera_event_to_dict(self):
        """Test camera event serialization to dictionary."""
        event = CameraEvent(
            event_type="queue_overflow",
            device_id="edge-001",
            confidence=0.85,
            bounding_box=[50, 300, 400, 200],
            person_count=5,
            metadata={"queue_length": 5}
        )

        event_dict = event.to_dict()

        assert event_dict["event_type"] == "queue_overflow"
        assert event_dict["device_id"] == "edge-001"
        assert event_dict["confidence"] == 0.85
        assert event_dict["person_count"] == 5
        assert event_dict["metadata"]["queue_length"] == 5

    def test_camera_event_backend_payload(self):
        """Test camera event payload formatting for backend."""
        event = CameraEvent(
            event_type="person_detected",
            device_id="edge-001",
            confidence=0.9,
            bounding_box=[100, 100, 50, 100],
            person_count=2
        )

        payload = event.to_backend_payload()

        # Should map to backend expected fields
        assert "camera_id" in payload  # device_id → camera_id
        assert payload["camera_id"] == "edge-001"
        assert "bbox_coordinates" in payload  # bounding_box → bbox_coordinates
        assert payload["bbox_coordinates"] == [100, 100, 50, 100]
        assert "details" in payload  # metadata → details
        assert "event_type" in payload
        assert "confidence" in payload

    def test_camera_event_with_snapshot(self):
        """Test camera event with base64 snapshot."""
        event = CameraEvent(
            event_type="theft_alert",
            device_id="edge-001",
            confidence=0.95,
            bounding_box=[200, 150, 80, 120],
            frame_base64="fake_base64_string"
        )

        payload = event.to_backend_payload()

        # Snapshot should be included as snapshot_url
        assert "snapshot_url" in payload
        assert payload["snapshot_url"].startswith("data:image/jpeg;base64,")


class TestSensorEvent:
    """Test sensor event data structure and payload formatting."""

    def test_sensor_event_creation(self):
        """Test basic sensor event creation."""
        event = SensorEvent(
            device_id="edge-001",
            sensor_id="edge-001_temp",
            sensor_type="temperature",
            value=24.5,
            unit="°C",
            is_anomaly=False
        )

        assert event.device_id == "edge-001"
        assert event.sensor_id == "edge-001_temp"  # Required field
        assert event.sensor_type == "temperature"
        assert event.value == 24.5
        assert event.unit == "°C"
        assert event.is_anomaly is False

    def test_sensor_event_to_dict(self):
        """Test sensor event serialization to dictionary."""
        event = SensorEvent(
            device_id="edge-001",
            sensor_id="edge-001_hum",
            sensor_type="humidity",
            value=65.0,
            unit="%",
            is_anomaly=False,
            threshold_min=30.0,
            threshold_max=70.0
        )

        event_dict = event.to_dict()

        assert event_dict["sensor_id"] == "edge-001_hum"
        assert event_dict["sensor_type"] == "humidity"
        assert event_dict["value"] == 65.0
        assert event_dict["unit"] == "%"
        assert event_dict["threshold_min"] == 30.0
        assert event_dict["threshold_max"] == 70.0

    def test_sensor_event_backend_payload(self):
        """Test sensor event payload formatting for backend."""
        event = SensorEvent(
            device_id="edge-001",
            sensor_id="edge-001_temp",
            sensor_type="temperature",
            value=28.5,
            unit="°C",
            is_anomaly=True,
            threshold_min=15.0,
            threshold_max=28.0,
            metadata={"location": "Store Floor"}
        )

        payload = event.to_backend_payload()

        # Should have required fields for backend
        assert "sensor_id" in payload  # Required by backend
        assert payload["sensor_id"] == "edge-001_temp"
        assert "device_id" in payload  # For device lookup
        assert "sensor_type" in payload
        assert "value" in payload
        assert "unit" in payload
        assert "threshold_min" in payload
        assert "threshold_max" in payload

        # Location should be extracted from metadata
        assert "location" in payload
        assert payload["location"] == "Store Floor"

    def test_sensor_event_with_metadata(self):
        """Test sensor event with additional metadata."""
        event = SensorEvent(
            device_id="edge-001",
            sensor_id="edge-001_weight",
            sensor_type="weight",
            value=15.5,
            unit="kg",
            metadata={"shelf_id": "A1", "location": "Back Store"}
        )

        payload = event.to_backend_payload()

        # Metadata should be flattened
        assert "location" in payload
        assert payload["location"] == "Back Store"
        assert "metadata_shelf_id" in payload
        assert payload["metadata_shelf_id"] == "A1"


class TestEventBuilder:
    """Test event builder factory methods."""

    @pytest.fixture
    def event_builder(self):
        """Create an event builder instance."""
        return EventBuilder(device_id="edge-001")

    def test_person_detected_event(self, event_builder):
        """Test person detected event building."""
        event = event_builder.person_detected(
            count=3,
            bbox=[100, 100, 50, 100],
            confidence=0.9
        )

        assert event.event_type == CameraEventType.PERSON_DETECTED
        assert event.person_count == 3
        assert event.bounding_box == [100, 100, 50, 100]
        assert event.confidence == 0.9

    def test_queue_overflow_event(self, event_builder):
        """Test queue overflow event building."""
        event = event_builder.queue_overflow(
            count=6,
            bbox=[50, 300, 400, 200],
            confidence=0.85
        )

        assert event.event_type == CameraEventType.QUEUE_OVERFLOW
        assert event.person_count == 6
        assert event.metadata["queue_length"] == 6

    def test_queue_empty_event(self, event_builder):
        """Test queue empty event building."""
        event = event_builder.queue_empty()

        assert event.event_type == CameraEventType.QUEUE_EMPTY
        assert event.person_count == 0
        assert event.metadata["queue_length"] == 0

    def test_out_of_stock_event(self, event_builder):
        """Test out of stock event building."""
        event = event_builder.out_of_stock(
            fill_percentage=5.0,
            shelf_zone_id="A1"
        )

        assert event.event_type == CameraEventType.OUT_OF_STOCK_DETECTED
        assert event.metadata["fill_percentage"] == 5.0
        assert event.metadata["shelf_zone"] == "A1"

    def test_temperature_reading_event(self, event_builder):
        """Test temperature reading event building."""
        event = event_builder.temperature_reading(
            sensor_id="edge-001_temp",
            celsius=22.5,
            is_anomaly=False
        )

        assert event.sensor_type == SensorType.TEMPERATURE
        assert event.sensor_id == "edge-001_temp"  # Required field
        assert event.value == 22.5
        assert event.unit == "°C"
        assert event.is_anomaly is False

    def test_ultrasonic_distance_event(self, event_builder):
        """Test ultrasonic distance reading event building."""
        event = event_builder.distance_reading(
            sensor_id="edge-001_ultrasonic",
            cm=85.5,
            sensor_type=SensorType.ULTRASONIC_DISTANCE
        )

        assert event.sensor_type == SensorType.ULTRASONIC_DISTANCE
        assert event.sensor_id == "edge-001_ultrasonic"
        assert event.value == 85.5
        assert event.unit == "cm"

    def test_footfall_event(self, event_builder):
        """Test footfall event building."""
        event = event_builder.footfall(
            entry_count=5,
            exit_count=3,
            current_occupancy=12
        )

        assert event.entry_count == 5
        assert event.exit_count == 3
        assert event.current_occupancy == 12

    def test_heartbeat_event(self, event_builder):
        """Test heartbeat event building."""
        event = event_builder.heartbeat(
            status="online",
            uptime_seconds=3600.0
        )

        assert event.device_id == "edge-001"
        assert event.status == "online"
        assert event.uptime_seconds == 3600.0
        # CPU and memory should be populated if psutil is available
        assert event.cpu_percent >= 0
        assert event.memory_percent >= 0


class TestEventPayloadBackendCompatibility:
    """Test that event payloads match backend API expectations."""

    def test_camera_event_vs_backend_fields(self):
        """Test camera event fields match backend CameraEvent model."""
        event = CameraEvent(
            event_type="person_detected",
            device_id="edge-001",
            confidence=0.9,
            bounding_box=[100, 100, 50, 100]
        )

        payload = event.to_backend_payload()

        # Backend expects: camera_id, event_type, confidence, bbox_coordinates, details
        assert "camera_id" in payload
        assert "event_type" in payload
        assert "confidence" in payload
        assert "bbox_coordinates" in payload
        assert "details" in payload

    def test_sensor_event_vs_backend_fields(self):
        """Test sensor event fields match backend SensorReading model."""
        event = SensorEvent(
            device_id="edge-001",
            sensor_id="edge-001_temp",
            sensor_type="temperature",
            value=24.5,
            unit="°C"
        )

        payload = event.to_backend_payload()

        # Backend expects: sensor_id, sensor_type, value, unit, device_id
        assert "sensor_id" in payload
        assert "sensor_type" in payload
        assert "value" in payload
        assert "unit" in payload
        assert "device_id" in payload

    def test_footfall_event_vs_backend_fields(self):
        """Test footfall event fields match backend Footfall model."""
        event = FootfallEvent(
            device_id="edge-001",
            entry_count=5,
            exit_count=2,
            current_occupancy=10
        )

        payload = event.to_backend_payload()

        # Backend expects: device_id, entry_count, exit_count, current_occupancy
        assert "device_id" in payload
        assert "entry_count" in payload
        assert "exit_count" in payload
        assert "current_occupancy" in payload


class TestDetection:
    """Test detection data structure."""

    def test_detection_creation(self):
        """Test detection object creation."""
        detection = Detection(
            class_id=0,
            class_name="person",
            confidence=0.95,
            bbox=[100, 100, 50, 100],
            center=(125, 150),
            track_id=1
        )

        assert detection.class_id == 0
        assert detection.class_name == "person"
        assert detection.confidence == 0.95
        assert detection.bbox == [100, 100, 50, 100]
        assert detection.center == (125, 150)
        assert detection.track_id == 1

    def test_detection_to_dict(self):
        """Test detection serialization."""
        detection = Detection(
            class_id=39,
            class_name="bottle",
            confidence=0.85,
            bbox=[200, 200, 30, 60],
            center=(215, 230)
        )

        detection_dict = detection.to_dict()

        assert detection_dict["class_id"] == 39
        assert detection_dict["class_name"] == "bottle"
        assert detection_dict["confidence"] == 0.85
        assert detection_dict["bbox"] == [200, 200, 30, 60]
        assert detection_dict["center"] == [215, 230]
        assert detection_dict["track_id"] is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
