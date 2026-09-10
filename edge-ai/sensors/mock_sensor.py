"""
Mock Sensor Reader — Simulated Hardware Sensor Data
Used when USE_MOCK_SENSORS=true (default) or when GPIO hardware is unavailable.

Generates realistic, slowly-varying sinusoidal values with noise:
  - Temperature: 18–26°C (ambient store environment)
  - Humidity: 40–70% RH
  - Weight: 0.5–5 kg (shelf load cell reading)
  - Distance IR: 10–100 cm (proximity)
  - PIR motion: random boolean

Useful for:
  - Local development without a Raspberry Pi
  - Demos and hackathon presentations
  - Unit testing without hardware dependency
"""

import math
import random
import time
from typing import Dict, Optional

from ..utils.logger import log_debug


class MockSensorReader:
    """
    Simulated sensor data generator using sinusoidal patterns + random noise.

    Produces repeatable, realistic-looking telemetry without any hardware.

    Args:
        seed: Random seed for reproducibility (optional).
    """

    def __init__(self, seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)

        self._start_time = time.time()

        # Phase offsets per sensor — so they don't all peak together
        self._phase = {
            "temperature": 0.0,
            "humidity": 1.0,
            "weight": 2.5,
            "ir_distance": 1.8,
        }

        # Motion history for PIR (simple state machine)
        self._pir_active = False
        self._pir_last_toggle = time.time()
        self._pir_cooldown = random.uniform(5, 30)

        log_debug("[MockSensor] Initialized — simulated sensor mode active")

    # ─────────────────────────────────────────────────────────────────────────
    # PRIMARY READ METHODS
    # ─────────────────────────────────────────────────────────────────────────

    def read_temperature(self) -> float:
        """
        Simulate DHT22 temperature reading.

        Returns:
            float: Temperature in Celsius (range: 18–26 °C)
        """
        elapsed = time.time() - self._start_time
        # Slow sinusoidal oscillation (period ~5 minutes) + noise
        base = 22.0
        amplitude = 4.0
        period_seconds = 300
        sin_val = math.sin(
            (2 * math.pi * elapsed / period_seconds) + self._phase["temperature"]
        )
        noise = random.gauss(0, 0.3)
        value = base + amplitude * sin_val + noise
        return round(value, 2)

    def read_humidity(self) -> float:
        """
        Simulate DHT22 humidity reading.

        Returns:
            float: Relative humidity in % (range: 40–70%)
        """
        elapsed = time.time() - self._start_time
        base = 55.0
        amplitude = 15.0
        period_seconds = 420  # Slightly different period from temp
        sin_val = math.sin(
            (2 * math.pi * elapsed / period_seconds) + self._phase["humidity"]
        )
        noise = random.gauss(0, 1.0)
        value = base + amplitude * sin_val + noise
        return round(max(30.0, min(80.0, value)), 2)

    def read_weight(self) -> float:
        """
        Simulate HX711 load cell (shelf weight) reading.

        Returns:
            float: Weight in kg (range: 0.5–5 kg)
        """
        elapsed = time.time() - self._start_time
        # Slow drop over time (simulates items being taken off shelf)
        base = 3.0
        trend = -0.001 * (elapsed % 3600)  # Slowly drop over 1 hour, then reset
        noise = random.gauss(0, 0.05)
        value = base + trend + noise
        return round(max(0.0, value), 3)

    def read_ir_distance(self) -> float:
        """
        Simulate IR proximity sensor reading.

        Returns:
            float: Distance in cm (range: 10–100 cm)
        """
        elapsed = time.time() - self._start_time
        base = 50.0
        amplitude = 35.0
        period_seconds = 60
        sin_val = math.sin(
            (2 * math.pi * elapsed / period_seconds) + self._phase["ir_distance"]
        )
        noise = random.gauss(0, 2.0)
        value = base + amplitude * sin_val + noise
        return round(max(5.0, min(200.0, value)), 2)

    def read_pir_motion(self) -> bool:
        """
        Simulate PIR motion sensor.

        Returns:
            bool: True if motion detected.
        """
        now = time.time()
        if now - self._pir_last_toggle > self._pir_cooldown:
            # Toggle state with 40% probability
            if random.random() < 0.4:
                self._pir_active = not self._pir_active
            self._pir_last_toggle = now
            self._pir_cooldown = random.uniform(3, 20)

        return self._pir_active

    def read_ultrasonic_distance(self) -> float:
        """
        Simulate HC-SR04 ultrasonic distance.

        Returns:
            float: Distance in cm (range: 5–300 cm)
        """
        base = 80.0
        noise = random.gauss(0, 5.0)
        return round(max(5.0, min(300.0, base + noise)), 2)

    # ─────────────────────────────────────────────────────────────────────────
    # BULK READ
    # ─────────────────────────────────────────────────────────────────────────

    def read_all(self) -> Dict[str, float]:
        """
        Read all sensors in one call.

        Returns:
            dict: {sensor_type: value}
        """
        readings = {
            "temperature": self.read_temperature(),
            "humidity": self.read_humidity(),
            "weight": self.read_weight(),
            "ir_distance": self.read_ir_distance(),
            "motion_pir": float(self.read_pir_motion()),
        }
        log_debug(f"[MockSensor] Readings: {readings}")
        return readings

    # ─────────────────────────────────────────────────────────────────────────
    # ANOMALY SIMULATION (for testing alert pipeline)
    # ─────────────────────────────────────────────────────────────────────────

    def inject_temperature_spike(self, celsius: float = 35.0) -> float:
        """Force a temperature anomaly reading (for testing alert pipeline)."""
        log_debug(f"[MockSensor] INJECTING temperature spike: {celsius}°C")
        return celsius

    def inject_humidity_drop(self, percent: float = 15.0) -> float:
        """Force a humidity anomaly reading."""
        log_debug(f"[MockSensor] INJECTING humidity drop: {percent}%")
        return percent

