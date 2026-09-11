"""
Sensor Sender — Timed Sensor Reading & Posting Loop
Runs in a background thread, reads all sensors every SENSOR_READ_INTERVAL_SECONDS,
builds SensorEvent objects via EventBuilder, and posts directly to backend.

Also handles IR footfall: periodically drains IR crossing counts and posts
a FootfallEvent to /monitoring/footfall.
"""

import threading
import time
from typing import Optional

from .sensor_manager import SensorManager
from ..events.event_builder import EventBuilder
from ..events.event_types import FootfallEvent
from ..utils.logger import log_info, log_warning, log_debug, log_error
from ..config import EdgeAIConfig


class SensorSender:
    """
    Background thread that reads sensors and posts to BIZmate backend.

    Args:
        sensor_manager: Initialized SensorManager instance.
        event_builder:  EventBuilder for constructing event objects.
        backend_client: BackendClient for posting events.
        read_interval:  Seconds between sensor read cycles.
        footfall_interval: Seconds between footfall drain cycles.
    """

    def __init__(
        self,
        sensor_manager: SensorManager,
        event_builder: EventBuilder,
        backend_client,
        read_interval: int = EdgeAIConfig.SENSOR_READ_INTERVAL_SECONDS,
        footfall_interval: int = 60,
    ):
        self._sensors = sensor_manager
        self._builder = event_builder
        self._client = backend_client
        self._read_interval = read_interval
        self._footfall_interval = footfall_interval

        self._running = False
        self._thread: Optional[threading.Thread] = None

        # Occupancy tracking
        self._current_occupancy = 0

        # Statistics
        self._total_readings_sent = 0
        self._total_footfall_sent = 0
        self._total_errors = 0

    # ─────────────────────────────────────────────────────────────────────────
    # PUBLIC API
    # ─────────────────────────────────────────────────────────────────────────

    def start(self):
        """Start the background sensor loop."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(
            target=self._run_loop,
            name="sensor-sender",
            daemon=True,
        )
        self._thread.start()
        log_info(
            f"[SensorSender] Started — "
            f"read_interval={self._read_interval}s, "
            f"footfall_interval={self._footfall_interval}s"
        )

    def stop(self):
        """Stop the sensor loop."""
        log_info("[SensorSender] Stopping...")
        self._running = False
        if self._thread:
            self._thread.join(timeout=self._read_interval + 5)
        log_info(
            f"[SensorSender] Stopped — "
            f"readings_sent={self._total_readings_sent}, "
            f"footfall_sent={self._total_footfall_sent}, "
            f"errors={self._total_errors}"
        )

    def stats(self) -> dict:
        """Return operational statistics."""
        return {
            "readings_sent": self._total_readings_sent,
            "footfall_sent": self._total_footfall_sent,
            "errors": self._total_errors,
            "current_occupancy": self._current_occupancy,
        }

    # ─────────────────────────────────────────────────────────────────────────
    # INTERNAL LOOP
    # ─────────────────────────────────────────────────────────────────────────

    def _run_loop(self):
        """Main sensor loop: read → build → post, with timed footfall drain."""
        last_footfall_post = time.time()

        while self._running:
            loop_start = time.time()

            # ── 1. Read all sensors ──────────────────────────────────────────
            try:
                readings = self._sensors.read_all()
                for reading in readings:
                    self._post_sensor_reading(reading)
            except Exception as e:
                self._total_errors += 1
                log_error(f"[SensorSender] read_all error: {e}")

            # ── 2. Drain footfall counts ────────────────────────────────────
            now = time.time()
            if now - last_footfall_post >= self._footfall_interval:
                try:
                    self._post_footfall()
                    last_footfall_post = now
                except Exception as e:
                    self._total_errors += 1
                    log_error(f"[SensorSender] footfall post error: {e}")

            # ── 3. Sleep remainder of interval ──────────────────────────────
            elapsed = time.time() - loop_start
            sleep_time = max(0, self._read_interval - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)

    def _post_sensor_reading(self, reading):
        """Build a SensorEvent from a SensorReading and post it."""
        try:
            event = self._builder.sensor_reading(
                sensor_type=reading.sensor_type,
                value=reading.value,
                unit=reading.unit,
                is_anomaly=reading.is_anomaly,
                threshold_min=reading.threshold_min,
                threshold_max=reading.threshold_max,
                metadata=reading.metadata,
            )
            success = self._client.post_sensor_reading(event)
            if success:
                self._total_readings_sent += 1
                if reading.is_anomaly:
                    log_warning(
                        f"[SensorSender] ANOMALY posted: "
                        f"{reading.sensor_type}={reading.value}{reading.unit} "
                        f"(range: {reading.threshold_min}–{reading.threshold_max})"
                    )
            else:
                self._total_errors += 1
        except Exception as e:
            self._total_errors += 1
            log_error(f"[SensorSender] Failed posting {reading.sensor_type}: {e}")

    def _post_footfall(self):
        """Drain IR counts and post a footfall event to backend."""
        counts = self._sensors.get_ir_counts()
        entry = counts.get("entry", 0)
        exit_ = counts.get("exit", 0)

        # Update live occupancy (clamp to 0)
        self._current_occupancy = max(0, self._current_occupancy + entry - exit_)

        if entry == 0 and exit_ == 0:
            log_debug("[SensorSender] No footfall changes this interval — skipping post")
            return

        event = self._builder.footfall(
            entry_count=entry,
            exit_count=exit_,
            current_occupancy=self._current_occupancy,
        )
        success = self._client.post_footfall(event)
        if success:
            self._sensors.reset_ir_counts()
            self._total_footfall_sent += 1
            log_debug(
                f"[SensorSender] Footfall posted: "
                f"entry={entry}, exit={exit_}, occupancy={self._current_occupancy}"
            )
        else:
            self._total_errors += 1
            log_warning("[SensorSender] Footfall post failed — counts preserved for retry")

