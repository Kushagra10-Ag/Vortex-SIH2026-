"""
Sensor Tests
Test sensor manager, individual sensors, and sensor reading functionality.
"""

import pytest
import time
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

import unittest.mock as mock


class TestSensorManager:
    """Test sensor manager functionality."""

    def test_sensor_manager_initialization(self):
        """Test sensor manager initialization with mock sensors."""
        from sensors.sensor_manager import SensorManager

        manager = SensorManager(use_mock=True)

        assert manager is not None
        assert manager._use_mock is True
        assert manager._ir is not None  # IR should be initialized
        assert manager._ultrasonic is not None  # Ultrasonic should be initialized

    def test_sensor_manager_read_all(self):
        """Test reading all sensors."""
        from sensors.sensor_manager import SensorManager

        manager = SensorManager(use_mock=True)
        readings = manager.read_all()

        assert isinstance(readings, list)
        # Should have temperature, humidity, weight, and ultrasonic readings
        assert len(readings) >= 2  # At minimum temp and humidity

    def test_sensor_manager_ir_counts(self):
        """Test IR footfall counting."""
        from sensors.sensor_manager import SensorManager

        manager = SensorManager(use_mock=True)

        # Get initial counts
        initial_counts = manager.get_ir_counts()
        assert "entry" in initial_counts
        assert "exit" in initial_counts

        # Reset counts
        manager.reset_ir_counts()
        reset_counts = manager.get_ir_counts()
        assert reset_counts["entry"] == 0
        assert reset_counts["exit"] == 0

    def test_sensor_manager_sensor_ids(self):
        """Test that sensor IDs are generated correctly."""
        from sensors.sensor_manager import SensorManager
        from config import EdgeAIConfig

        manager = SensorManager(use_mock=True)

        # Check that sensor IDs are based on device ID
        expected_device_id = EdgeAIConfig.DEVICE_ID
        assert manager._sensor_ids["temperature"] == f"{expected_device_id}_temp"
        assert manager._sensor_ids["humidity"] == f"{expected_device_id}_hum"
        assert manager._sensor_ids["weight"] == f"{expected_device_id}_weight"
        assert manager._sensor_ids["ultrasonic"] == f"{expected_device_id}_ultrasonic"

    def test_sensor_reading_structure(self):
        """Test that sensor readings have required fields."""
        from sensors.sensor_manager import SensorManager, SensorReading

        manager = SensorManager(use_mock=True)
        readings = manager.read_all()

        for reading in readings:
            assert isinstance(reading, SensorReading)
            assert hasattr(reading, 'sensor_id')
            assert hasattr(reading, 'sensor_type')
            assert hasattr(reading, 'value')
            assert hasattr(reading, 'unit')
            assert hasattr(reading, 'is_anomaly')
            # sensor_id should be present (required by backend)
            assert reading.sensor_id is not None
            assert reading.sensor_id != ""


class TestUltrasonicSensor:
    """Test ultrasonic sensor functionality."""

    def test_ultrasonic_initialization(self):
        """Test ultrasonic sensor initialization."""
        from sensors.ultrasonic_sensor import UltrasonicSensorReader

        sensor = UltrasonicSensorReader(
            trig_pin=23,
            echo_pin=24,
            use_mock=True,
            shelf_mode=True
        )

        assert sensor is not None
        assert sensor.use_mock is True
        assert sensor.shelf_mode is True

    def test_ultrasonic_distance_reading(self):
        """Test ultrasonic distance reading."""
        from sensors.ultrasonic_sensor import UltrasonicSensorReader

        sensor = UltrasonicSensorReader(
            trig_pin=23,
            echo_pin=24,
            use_mock=True
        )

        distance = sensor.read_distance()

        assert distance is not None
        assert isinstance(distance, float)
        assert 5.0 <= distance <= 300.0  # Valid range

    def test_ultrasonic_fill_percentage_calculation(self):
        """Test shelf fill percentage calculation."""
        from sensors.ultrasonic_sensor import UltrasonicSensorReader

        sensor = UltrasonicSensorReader(
            trig_pin=23,
            echo_pin=24,
            use_mock=True,
            shelf_mode=True,
            empty_distance_cm=150.0,
            full_distance_cm=30.0
        )

        # Test fill percentage calculation
        # At full distance (30cm) should be 100% full
        fill_full = sensor.calculate_fill_percentage(30.0)
        assert fill_full == 100.0

        # At empty distance (150cm) should be 0% full
        fill_empty = sensor.calculate_fill_percentage(150.0)
        assert fill_empty == 0.0

        # At midpoint should be ~50%
        fill_half = sensor.calculate_fill_percentage(90.0)
        assert 45.0 <= fill_half <= 55.0

    def test_ultrasonic_fill_percentage_clamping(self):
        """Test that fill percentage is clamped to 0-100."""
        from sensors.ultrasonic_sensor import UltrasonicSensorReader

        sensor = UltrasonicSensorReader(
            trig_pin=23,
            echo_pin=24,
            use_mock=True,
            shelf_mode=True,
            empty_distance_cm=150.0,
            full_distance_cm=30.0
        )

        # Below full distance should cap at 100%
        fill_below = sensor.calculate_fill_percentage(10.0)
        assert fill_below == 100.0

        # Above empty distance should cap at 0%
        fill_above = sensor.calculate_fill_percentage(200.0)
        assert fill_above == 0.0


class TestIRSensor:
    """Test IR sensor functionality."""

    def test_ir_sensor_initialization(self):
        """Test IR sensor initialization."""
        from sensors.ir_sensor import IRSensorReader

        sensor = IRSensorReader(
            pin=27,
            use_mock=True
        )

        assert sensor is not None
        assert sensor.use_mock is True

    def test_ir_sensor_beam_reading(self):
        """Test IR beam state reading."""
        from sensors.ir_sensor import IRSensorReader

        sensor = IRSensorReader(
            pin=27,
            use_mock=True
        )

        # Beam state should be boolean
        beam_broken = sensor.read_beam_broken()
        assert isinstance(beam_broken, bool)

    def test_ir_sensor_crossing_detection(self):
        """Test IR crossing detection."""
        from sensors.ir_sensor import IRSensorReader

        sensor = IRSensorReader(
            pin=27,
            use_mock=True
        )

        # Crossing detection should return 'entry', 'exit', or None
        crossing = sensor.check_crossing()
        assert crossing in ['entry', 'exit', None]

    def test_ir_sensor_70_30_ratio(self):
        """Test that mock mode simulates 70% entry / 30% exit ratio."""
        from sensors.ir_sensor import IRSensorReader

        sensor = IRSensorReader(
            pin=27,
            use_mock=True
        )

        # Simulate multiple crossings
        crossings = []
        for _ in range(100):
            crossing = sensor.check_crossing()
            if crossing:
                crossings.append(crossing)
            time.sleep(0.01)  # Small delay between checks

        # Check ratio (with some tolerance)
        if len(crossings) > 10:  # Only test if we got enough crossings
            entry_count = crossings.count('entry')
            exit_count = crossings.count('exit')
            total = entry_count + exit_count

            entry_ratio = entry_count / total if total > 0 else 0
            # Should be approximately 70% (allow 60-80% range)
            assert 0.60 <= entry_ratio <= 0.80

    def test_ir_sensor_counts_reset(self):
        """Test IR count reset functionality."""
        from sensors.ir_sensor import IRSensorReader

        sensor = IRSensorReader(
            pin=27,
            use_mock=True
        )

        # Generate some crossings
        for _ in range(10):
            sensor.check_crossing()
            time.sleep(0.01)

        counts = sensor.get_counts()
        assert counts["entry"] >= 0 or counts["exit"] >= 0

        # Reset counts
        sensor.reset_counts()
        reset_counts = sensor.get_counts()
        assert reset_counts["entry"] == 0
        assert reset_counts["exit"] == 0


class TestMockSensor:
    """Test mock sensor functionality."""

    def test_mock_sensor_temperature(self):
        """Test mock temperature sensor."""
        from sensors.mock_sensor import MockSensorReader

        mock = MockSensorReader()
        temp = mock.read_temperature()

        assert temp is not None
        assert isinstance(temp, float)
        assert 15.0 <= temp <= 35.0  # Reasonable temperature range

    def test_mock_sensor_humidity(self):
        """Test mock humidity sensor."""
        from sensors.mock_sensor import MockSensorReader

        mock = MockSensorReader()
        humidity = mock.read_humidity()

        assert humidity is not None
        assert isinstance(humidity, float)
        assert 20.0 <= humidity <= 80.0  # Reasonable humidity range

    def test_mock_sensor_weight(self):
        """Test mock weight sensor."""
        from sensors.mock_sensor import MockSensorReader

        mock = MockSensorReader()
        weight = mock.read_weight()

        assert weight is not None
        assert isinstance(weight, float)
        assert 0.0 <= weight <= 50.0  # Reasonable weight range


class TestSensorThresholds:
    """Test sensor threshold checking."""

    def test_temperature_thresholds(self):
        """Test temperature anomaly detection."""
        from sensors.sensor_manager import SensorManager
        from utils.constants import SensorThresholds

        manager = SensorManager(use_mock=True)
        readings = manager.read_all()

        temp_reading = next((r for r in readings if r.sensor_type == "temperature"), None)
        if temp_reading:
            # Check that thresholds are applied
            assert temp_reading.threshold_min == SensorThresholds.TEMPERATURE_AMBIENT_MIN
            assert temp_reading.threshold_max == SensorThresholds.TEMPERATURE_AMBIENT_MAX

    def test_humidity_thresholds(self):
        """Test humidity anomaly detection."""
        from sensors.sensor_manager import SensorManager
        from utils.constants import SensorThresholds

        manager = SensorManager(use_mock=True)
        readings = manager.read_all()

        humidity_reading = next((r for r in readings if r.sensor_type == "humidity"), None)
        if humidity_reading:
            # Check that thresholds are applied
            assert humidity_reading.threshold_min == SensorThresholds.HUMIDITY_MIN
            assert humidity_reading.threshold_max == SensorThresholds.HUMIDITY_MAX

    def test_distance_thresholds(self):
        """Test ultrasonic distance thresholds."""
        from sensors.sensor_manager import SensorManager
        from utils.constants import SensorThresholds

        manager = SensorManager(use_mock=True)
        readings = manager.read_all()

        distance_reading = next((r for r in readings if r.sensor_type == "ultrasonic_distance"), None)
        if distance_reading:
            # Check that thresholds are applied
            assert distance_reading.threshold_min == SensorThresholds.DISTANCE_MIN
            assert distance_reading.threshold_max == SensorThresholds.DISTANCE_MAX


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
