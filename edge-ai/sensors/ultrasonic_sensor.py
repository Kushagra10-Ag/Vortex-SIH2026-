"""
Ultrasonic Sensor Reader — HC-SR04 Distance Measurement
Reads distance from HC-SR04 ultrasonic sensor via GPIO TRIG/ECHO pins.

Hardware: HC-SR04 connected to Raspberry Pi GPIO.
Simulated: Falls back to mock values when GPIO is unavailable.

Physics:
  - Send 10µs TRIG pulse → sensor emits 40kHz burst
  - Measure ECHO pulse width → distance = (pulse_width × speed_of_sound) / 2
  - Speed of sound ≈ 34300 cm/s at 20°C
"""

import time
from typing import Optional

from ..utils.logger import log_info, log_warning, log_debug, log_error
from ..config import EdgeAIConfig

# Graceful import — only works on Raspberry Pi
try:
    import RPi.GPIO as GPIO
    _GPIO_AVAILABLE = True
    log_info("[Ultrasonic] RPi.GPIO detected — hardware mode active")
except ImportError:
    _GPIO_AVAILABLE = False

# Speed of sound in cm/s at ~20°C
_SPEED_OF_SOUND_CM_S = 34300.0

# Max measurement timeout (seconds) — avoids blocking if ECHO never returns
_ECHO_TIMEOUT = 0.025   # 25ms → max ~4m distance before timeout


class UltrasonicSensorReader:
    """
    HC-SR04 ultrasonic distance sensor reader.

    Can be used for:
      - Shelf fill level estimation (top-down mount)
      - Doorway proximity / footfall trigger
      - Obstacle detection

    Args:
        trig_pin:        GPIO BCM pin connected to TRIG
        echo_pin:        GPIO BCM pin connected to ECHO
        num_samples:     Number of readings to average per measurement
        sample_delay:    Seconds between samples in multi-sample mode
        use_mock:        Force mock mode
    """

    def __init__(
        self,
        trig_pin: int = EdgeAIConfig.ULTRASONIC_TRIG_PIN,
        echo_pin: int = EdgeAIConfig.ULTRASONIC_ECHO_PIN,
        num_samples: int = 3,
        sample_delay: float = 0.05,
        use_mock: bool = not _GPIO_AVAILABLE,
    ):
        self.trig_pin = trig_pin
        self.echo_pin = echo_pin
        self.num_samples = num_samples
        self.sample_delay = sample_delay
        self.use_mock = use_mock or not _GPIO_AVAILABLE

        self._last_reading: Optional[float] = None

        if not self.use_mock:
            self._init_gpio()
        else:
            log_debug(
                f"[Ultrasonic] Mock mode — trig={trig_pin}, echo={echo_pin}"
            )

    def _init_gpio(self):
        """Initialize GPIO pins for HC-SR04."""
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.trig_pin, GPIO.OUT)
            GPIO.setup(self.echo_pin, GPIO.IN)
            GPIO.output(self.trig_pin, GPIO.LOW)
            time.sleep(0.1)  # Settle time
            log_info(
                f"[Ultrasonic] GPIO initialized — TRIG={self.trig_pin}, "
                f"ECHO={self.echo_pin}"
            )
        except Exception as e:
            log_warning(f"[Ultrasonic] GPIO init failed ({e}) — falling back to mock")
            self.use_mock = True

    # ─────────────────────────────────────────────────────────────────────────
    # PUBLIC API
    # ─────────────────────────────────────────────────────────────────────────

    def read_distance(self) -> Optional[float]:
        """
        Take a single distance measurement.

        Returns:
            float: Distance in cm, or None if measurement failed.
        """
        if self.use_mock:
            return self._mock_distance()

        return self._measure_single()

    def read_distance_averaged(self) -> Optional[float]:
        """
        Take multiple readings and return the median (more stable).

        Returns:
            float: Median distance in cm, or None if all failed.
        """
        if self.use_mock:
            return self._mock_distance()

        readings = []
        for _ in range(self.num_samples):
            dist = self._measure_single()
            if dist is not None:
                readings.append(dist)
            time.sleep(self.sample_delay)

        if not readings:
            log_warning("[Ultrasonic] All samples failed")
            return None

        # Return median
        readings.sort()
        mid = len(readings) // 2
        result = readings[mid]
        self._last_reading = result
        log_debug(f"[Ultrasonic] Averaged reading: {result:.1f} cm (n={len(readings)})")
        return result

    @property
    def last_reading(self) -> Optional[float]:
        """Return the most recent valid reading."""
        return self._last_reading

    def cleanup(self):
        """Release GPIO resources."""
        if not self.use_mock and _GPIO_AVAILABLE:
            try:
                GPIO.cleanup([self.trig_pin, self.echo_pin])
                log_debug("[Ultrasonic] GPIO cleaned up")
            except Exception:
                pass

    # ─────────────────────────────────────────────────────────────────────────
    # INTERNAL — HARDWARE MEASUREMENT
    # ─────────────────────────────────────────────────────────────────────────

    def _measure_single(self) -> Optional[float]:
        """
        Perform one HC-SR04 measurement cycle.

        Returns:
            float: Distance in cm, or None on timeout/error.
        """
        try:
            # Send 10µs TRIG pulse
            GPIO.output(self.trig_pin, GPIO.LOW)
            time.sleep(0.000002)   # 2µs settle
            GPIO.output(self.trig_pin, GPIO.HIGH)
            time.sleep(0.00001)    # 10µs pulse
            GPIO.output(self.trig_pin, GPIO.LOW)

            # Wait for ECHO to go HIGH
            pulse_start = time.time()
            timeout_start = pulse_start
            while GPIO.input(self.echo_pin) == GPIO.LOW:
                pulse_start = time.time()
                if pulse_start - timeout_start > _ECHO_TIMEOUT:
                    log_debug("[Ultrasonic] ECHO start timeout")
                    return None

            # Wait for ECHO to go LOW
            pulse_end = time.time()
            while GPIO.input(self.echo_pin) == GPIO.HIGH:
                pulse_end = time.time()
                if pulse_end - pulse_start > _ECHO_TIMEOUT:
                    log_debug("[Ultrasonic] ECHO end timeout")
                    return None

            # Calculate distance
            duration = pulse_end - pulse_start
            distance_cm = (duration * _SPEED_OF_SOUND_CM_S) / 2.0

            # Sanity check (HC-SR04 reliable range: 2–400 cm)
            if 2.0 <= distance_cm <= 400.0:
                self._last_reading = distance_cm
                return round(distance_cm, 2)
            else:
                log_debug(f"[Ultrasonic] Out-of-range reading: {distance_cm:.1f} cm")
                return None

        except Exception as e:
            log_error(f"[Ultrasonic] Measurement error: {e}")
            return None

    # ─────────────────────────────────────────────────────────────────────────
    # INTERNAL — MOCK
    # ─────────────────────────────────────────────────────────────────────────

    def _mock_distance(self) -> float:
        """
        Generate realistic ultrasonic distance reading.

        Simulates a shelf with varying fill level (40–150 cm range).

        Returns:
            float: Simulated distance in cm.
        """
        import random
        import math

        elapsed = time.time() % 600  # 10-minute cycle
        # Distance slowly changes as items are added/removed from shelf
        base = 80.0
        variation = 40.0 * math.sin(2 * math.pi * elapsed / 600)
        noise = random.gauss(0, 1.5)
        value = base + variation + noise
        value = max(5.0, min(300.0, value))
        self._last_reading = round(value, 2)
        return self._last_reading

