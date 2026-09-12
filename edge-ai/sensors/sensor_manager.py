"""
Sensor Manager — Central Coordinator for All IoT Sensors
Initializes the correct sensor readers based on config, reads all sensors,
checks readings against thresholds, and returns structured results.

Design:
  - One SensorManager per edge device
  - Supports mixed real/mock sensors (e.g., real DHT22 + mock weight)
  - Returns anomaly flags for each reading (backend auto-creates alerts)
  - Thread-safe: read_all() can be called from sensor_sender thread
"""

from typing import Dict, Optional, List, Any
from dataclasses import dataclass, field

from .mock_sensor import MockSensorReader
from .ir_sensor import IRSensorReader
from .ultrasonic_sensor import UltrasonicSensorReader
from ..utils.constants import SensorThresholds, SensorType
from ..utils.logger import log_info, log_warning, log_debug, log_error
from ..config import EdgeAIConfig


@dataclass
class SensorReading:
    """
    A single processed sensor reading with threshold/anomaly metadata.

    Attributes:
        sensor_id:      Unique sensor identifier (required by backend)
        sensor_type:    SensorType constant string
        value:          Numeric reading
        unit:           Unit of measurement
        is_anomaly:     True if value is outside threshold range
        threshold_min:  Lower bound (from SensorThresholds)
        threshold_max:  Upper bound (from SensorThresholds)
        metadata:       Extra context (gpio pin, location, etc.)
    """
    sensor_id: str
    sensor_type: str
    value: float
    unit: str
    is_anomaly: bool = False
    threshold_min: Optional[float] = None
    threshold_max: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class SensorManager:
    """
    Manages all sensor readers and provides a unified read_all() interface.

    Initializes sensors based on EdgeAIConfig flags:
      - ENABLE_DHT22      → real DHT22 if available, else mock
      - ENABLE_HX711      → real HX711 if available, else mock
      - ENABLE_PIR        → real PIR if available, else mock
      - ENABLE_ULTRASONIC → real HC-SR04 if available, else mock
      - USE_MOCK_SENSORS  → forces mock for all sensors

    Args:
        use_mock:  Override to force mock mode for all sensors.
    """

    def __init__(self, use_mock: Optional[bool] = None):
        # Determine mock mode
        force_mock = use_mock if use_mock is not None else EdgeAIConfig.USE_MOCK_SENSORS

        # Always initialize mock reader (fallback + DHT22/HX711 simulation)
        self._mock = MockSensorReader()

        # IR sensor (footfall counter)
        self._ir: Optional[IRSensorReader] = None
        if EdgeAIConfig.ENABLE_PIR or force_mock:
            self._ir = IRSensorReader(
                pin=EdgeAIConfig.PIR_PIN,
                use_mock=force_mock,
            )

        # Ultrasonic (shelf fill / proximity)
        self._ultrasonic: Optional[UltrasonicSensorReader] = None
        if EdgeAIConfig.ENABLE_ULTRASONIC or force_mock:
            self._ultrasonic = UltrasonicSensorReader(
                trig_pin=EdgeAIConfig.ULTRASONIC_TRIG_PIN,
                echo_pin=EdgeAIConfig.ULTRASONIC_ECHO_PIN,
                use_mock=force_mock,
                shelf_mode=True,  # Enable shelf fill calculation
                empty_distance_cm=150.0,
                full_distance_cm=30.0,
            )

        # DHT22 — try real hardware, fall back to mock
        self._dht22_reader = None
        if EdgeAIConfig.ENABLE_DHT22 and not force_mock:
            self._dht22_reader = self._init_dht22()

        # HX711 — try real hardware, fall back to mock
        self._hx711_reader = None
        if EdgeAIConfig.ENABLE_HX711 and not force_mock:
            self._hx711_reader = self._init_hx711()

        self._use_mock = force_mock

        # Generate sensor IDs based on device ID
        self._device_id = EdgeAIConfig.DEVICE_ID
        self._sensor_ids = {
            "temperature": f"{self._device_id}_temp",
            "humidity": f"{self._device_id}_hum",
            "weight": f"{self._device_id}_weight",
            "ultrasonic": f"{self._device_id}_ultrasonic",
        }

        log_info(
            f"[SensorManager] Initialized — "
            f"mock={force_mock}, "
            f"dht22={'real' if self._dht22_reader else 'mock'}, "
            f"hx711={'real' if self._hx711_reader else 'mock'}, "
            f"ir={'enabled' if self._ir else 'disabled'}, "
            f"ultrasonic={'enabled' if self._ultrasonic else 'disabled'}"
        )

    # ─────────────────────────────────────────────────────────────────────────
    # PUBLIC API
    # ─────────────────────────────────────────────────────────────────────────

    def read_all(self) -> List[SensorReading]:
        """
        Read all configured sensors and check against thresholds.

        Returns:
            List[SensorReading]: One entry per sensor type.
        """
        readings: List[SensorReading] = []

        # Temperature
        temp = self._read_temperature()
        if temp is not None:
            readings.append(temp)

        # Humidity
        hum = self._read_humidity()
        if hum is not None:
            readings.append(hum)

        # Shelf weight (HX711 or mock)
        weight = self._read_weight()
        if weight is not None:
            readings.append(weight)

        # Ultrasonic distance
        if self._ultrasonic:
            dist = self._read_ultrasonic()
            if dist is not None:
                readings.append(dist)

        log_debug(
            f"[SensorManager] read_all() → {len(readings)} readings, "
            f"{sum(1 for r in readings if r.is_anomaly)} anomalies"
        )
        return readings

    def read_ir_crossing(self) -> Optional[str]:
        """
        Check IR sensor for a crossing event.

        Returns:
            'entry' | 'exit' | None
        """
        if self._ir:
            return self._ir.check_crossing()
        return None

    def get_ir_counts(self) -> Dict[str, int]:
        """Return accumulated entry/exit counts from IR sensor."""
        if self._ir:
            return self._ir.get_counts()
        return {"entry": 0, "exit": 0}

    def reset_ir_counts(self):
        """Reset IR footfall counters after posting to backend."""
        if self._ir:
            self._ir.reset_counts()

    def cleanup(self):
        """Release all GPIO and hardware resources."""
        if self._ir:
            self._ir.cleanup()
        if self._ultrasonic:
            self._ultrasonic.cleanup()
        log_info("[SensorManager] Cleaned up")

    # ─────────────────────────────────────────────────────────────────────────
    # PRIVATE — PER-SENSOR READERS
    # ─────────────────────────────────────────────────────────────────────────

    def _read_temperature(self) -> Optional[SensorReading]:
        """Read temperature from DHT22 or mock."""
        try:
            if self._dht22_reader:
                humidity, temp = self._dht22_reader.read_retry(
                    EdgeAIConfig.DHT22_PIN, retries=3
                )
                if temp is None:
                    log_warning("[SensorManager] DHT22 temp read failed — using mock")
                    temp = self._mock.read_temperature()
            else:
                temp = self._mock.read_temperature()

            is_anomaly = not (
                SensorThresholds.TEMPERATURE_AMBIENT_MIN
                <= temp
                <= SensorThresholds.TEMPERATURE_AMBIENT_MAX
            )

            return SensorReading(
                sensor_id=self._sensor_ids["temperature"],
                sensor_type=SensorType.TEMPERATURE,
                value=round(temp, 2),
                unit="°C",
                is_anomaly=is_anomaly,
                threshold_min=SensorThresholds.TEMPERATURE_AMBIENT_MIN,
                threshold_max=SensorThresholds.TEMPERATURE_AMBIENT_MAX,
            )
        except Exception as e:
            log_error(f"[SensorManager] Temperature read error: {e}")
            return None

    def _read_humidity(self) -> Optional[SensorReading]:
        """Read humidity from DHT22 or mock."""
        try:
            if self._dht22_reader:
                humidity, temp = self._dht22_reader.read_retry(
                    EdgeAIConfig.DHT22_PIN, retries=3
                )
                if humidity is None:
                    humidity = self._mock.read_humidity()
            else:
                humidity = self._mock.read_humidity()

            is_anomaly = not (
                SensorThresholds.HUMIDITY_MIN
                <= humidity
                <= SensorThresholds.HUMIDITY_MAX
            )

            return SensorReading(
                sensor_id=self._sensor_ids["humidity"],
                sensor_type=SensorType.HUMIDITY,
                value=round(humidity, 2),
                unit="%",
                is_anomaly=is_anomaly,
                threshold_min=SensorThresholds.HUMIDITY_MIN,
                threshold_max=SensorThresholds.HUMIDITY_MAX,
            )
        except Exception as e:
            log_error(f"[SensorManager] Humidity read error: {e}")
            return None

    def _read_weight(self) -> Optional[SensorReading]:
        """Read shelf weight from HX711 or mock."""
        try:
            if self._hx711_reader:
                try:
                    weight_kg = self._hx711_reader.get_weight_mean(20) / 1000.0
                except Exception:
                    weight_kg = self._mock.read_weight()
            else:
                weight_kg = self._mock.read_weight()

            is_anomaly = not (
                SensorThresholds.WEIGHT_MIN
                <= weight_kg
                <= SensorThresholds.WEIGHT_MAX
            )

            return SensorReading(
                sensor_id=self._sensor_ids["weight"],
                sensor_type=SensorType.WEIGHT,
                value=round(weight_kg, 3),
                unit="kg",
                is_anomaly=is_anomaly,
                threshold_min=SensorThresholds.WEIGHT_MIN,
                threshold_max=SensorThresholds.WEIGHT_MAX,
            )
        except Exception as e:
            log_error(f"[SensorManager] Weight read error: {e}")
            return None

    def _read_ultrasonic(self) -> Optional[SensorReading]:
        """Read distance from ultrasonic sensor."""
        try:
            dist = self._ultrasonic.read_distance_averaged()
            if dist is None:
                return None

            is_anomaly = not (
                SensorThresholds.DISTANCE_MIN
                <= dist
                <= SensorThresholds.DISTANCE_MAX
            )

            # Calculate fill percentage if in shelf mode
            metadata = {}
            if self._ultrasonic.shelf_mode:
                fill_pct = self._ultrasonic.calculate_fill_percentage(dist)
                if fill_pct is not None:
                    metadata["fill_percentage"] = round(fill_pct, 2)

            return SensorReading(
                sensor_id=self._sensor_ids["ultrasonic"],
                sensor_type=SensorType.ULTRASONIC_DISTANCE,
                value=dist,
                unit="cm",
                is_anomaly=is_anomaly,
                threshold_min=SensorThresholds.DISTANCE_MIN,
                threshold_max=SensorThresholds.DISTANCE_MAX,
                metadata=metadata,
            )
        except Exception as e:
            log_error(f"[SensorManager] Ultrasonic read error: {e}")
            return None

    # ─────────────────────────────────────────────────────────────────────────
    # HARDWARE INIT HELPERS (graceful failure)
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    def _init_dht22():
        """Try to import Adafruit_DHT. Returns reader or None."""
        try:
            import Adafruit_DHT
            log_info("[SensorManager] Adafruit_DHT found — DHT22 hardware mode")
            return Adafruit_DHT.DHT22
        except ImportError:
            log_warning(
                "[SensorManager] Adafruit_DHT not installed — DHT22 in mock mode"
            )
            return None

    @staticmethod
    def _init_hx711():
        """Try to import hx711. Returns reader or None."""
        try:
            from hx711 import HX711
            hx = HX711(
                dout_pin=EdgeAIConfig.HX711_DATA_PIN,
                pd_sck_pin=EdgeAIConfig.HX711_CLOCK_PIN,
            )
            hx.reset()
            hx.tare()
            log_info("[SensorManager] HX711 initialized — load cell hardware mode")
            return hx
        except ImportError:
            log_warning("[SensorManager] hx711 not installed — weight in mock mode")
            return None
        except Exception as e:
            log_warning(f"[SensorManager] HX711 init failed ({e}) — mock mode")
            return None

