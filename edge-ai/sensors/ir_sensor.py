"""
IR Sensor Reader — Footfall Counter via IR Beam
Reads an IR proximity sensor to detect people crossing the store entrance.

Hardware: GPIO-connected IR break-beam or reflective IR sensor.
Simulated: Falls back to mock values when GPIO is unavailable.

Logic:
  - When IR beam is broken (object detected within threshold distance): entry event
  - Direction detection (optional): second IR sensor for entry vs exit
  - Debounce: minimum 0.5s between events to filter noise
  - Mock mode: Simulates 70% entry / 30% exit ratio for testing
"""

import time
import random
from typing import Optional

from utils.logger import log_info, log_warning, log_debug
from config import EdgeAIConfig

# Graceful import — RPi.GPIO only available on Raspberry Pi
try:
    import RPi.GPIO as GPIO
    _GPIO_AVAILABLE = True
    log_info("[IRSensor] RPi.GPIO detected — hardware mode active")
except ImportError:
    _GPIO_AVAILABLE = False
    log_warning("[IRSensor] RPi.GPIO not available — using mock mode")


class IRSensorReader:
    """
    IR proximity sensor reader for footfall counting.

    Counts entry and exit events via IR beam interruption.
    Works in real GPIO mode on Raspberry Pi, or mock mode for testing.

    Args:
        pin:               GPIO BCM pin number for IR sensor data line
        threshold_cm:      Maximum distance (cm) to count as "beam broken"
        debounce_seconds:  Minimum time between consecutive detection events
        use_mock:          Force mock mode regardless of GPIO availability
    """

    def __init__(
        self,
        pin: int = EdgeAIConfig.PIR_PIN,
        threshold_cm: float = 30.0,
        debounce_seconds: float = 0.5,
        use_mock: bool = not _GPIO_AVAILABLE,
    ):
        self.pin = pin
        self.threshold_cm = threshold_cm
        self.debounce_seconds = debounce_seconds
        self.use_mock = use_mock or not _GPIO_AVAILABLE

        # Counters
        self._entry_count = 0
        self._exit_count = 0
        self._last_event_time = 0.0
        self._last_state = False  # False = beam clear, True = beam broken

        # Mock state
        self._mock_last_trigger = time.time()
        self._mock_trigger_interval = 15.0  # seconds between mock detections

        if not self.use_mock:
            self._init_gpio()
        else:
            log_debug(f"[IRSensor] Mock mode — pin {self.pin}")

    def _init_gpio(self):
        """Initialize GPIO pin for hardware IR sensor."""
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            log_info(f"[IRSensor] GPIO initialized on pin {self.pin}")
        except Exception as e:
            log_warning(f"[IRSensor] GPIO init failed ({e}) — falling back to mock")
            self.use_mock = True

    # ─────────────────────────────────────────────────────────────────────────
    # PUBLIC API
    # ─────────────────────────────────────────────────────────────────────────

    def read_beam_broken(self) -> bool:
        """
        Check if IR beam is currently broken (object detected).

        Returns:
            bool: True if beam is broken (object/person in path)
        """
        if self.use_mock:
            return self._mock_beam_state()

        try:
            # GPIO.LOW = beam broken (active-low IR sensor)
            raw = GPIO.input(self.pin)
            return raw == GPIO.LOW
        except Exception as e:
            log_warning(f"[IRSensor] Read error: {e}")
            return False

    def check_crossing(self) -> Optional[str]:
        """
        Poll the sensor and return crossing event type if detected.

        Call this frequently (every ~50ms) in your sensor loop.

        Returns:
            'entry' if entry detected, 'exit' if exit detected, None otherwise.
            (Simple single-sensor mode: every crossing is counted as 'entry')
            (Mock mode: 70% entry / 30% exit ratio for testing)
        """
        now = time.time()
        beam_broken = self.read_beam_broken()

        # Detect rising edge (clear → broken) with debounce
        if beam_broken and not self._last_state:
            if now - self._last_event_time >= self.debounce_seconds:
                self._last_event_time = now
                self._last_state = True

                # In mock mode, simulate 70% entry / 30% exit ratio
                if self.use_mock:
                    event_type = "entry" if random.random() < 0.7 else "exit"
                    if event_type == "entry":
                        self._entry_count += 1
                        log_debug(
                            f"[IRSensor] Mock entry detected (total entries: {self._entry_count})"
                        )
                    else:
                        self._exit_count += 1
                        log_debug(
                            f"[IRSensor] Mock exit detected (total exits: {self._exit_count})"
                        )
                    return event_type
                else:
                    # Hardware mode: single sensor = entry only
                    self._entry_count += 1
                    log_debug(
                        f"[IRSensor] Person crossing detected (total entries: {self._entry_count})"
                    )
                    return "entry"

        elif not beam_broken and self._last_state:
            # Beam cleared
            self._last_state = False

        return None

    def get_counts(self) -> dict:
        """
        Return accumulated entry/exit counts since last reset.

        Returns:
            dict: {'entry': int, 'exit': int}
        """
        return {
            "entry": self._entry_count,
            "exit": self._exit_count,
        }

    def reset_counts(self):
        """Reset entry and exit counters (call after posting to backend)."""
        self._entry_count = 0
        self._exit_count = 0

    def cleanup(self):
        """Release GPIO resources."""
        if not self.use_mock and _GPIO_AVAILABLE:
            try:
                GPIO.cleanup(self.pin)
                log_debug(f"[IRSensor] GPIO pin {self.pin} cleaned up")
            except Exception:
                pass

    # ─────────────────────────────────────────────────────────────────────────
    # MOCK INTERNAL
    # ─────────────────────────────────────────────────────────────────────────

    def _mock_beam_state(self) -> bool:
        """
        Simulate IR beam breaking with periodic triggers.

        Returns:
            bool: True approximately every mock_trigger_interval seconds.
        """
        import random
        now = time.time()
        if now - self._mock_last_trigger > self._mock_trigger_interval:
            self._mock_last_trigger = now
            self._mock_trigger_interval = random.uniform(8, 30)
            return True
        return False

