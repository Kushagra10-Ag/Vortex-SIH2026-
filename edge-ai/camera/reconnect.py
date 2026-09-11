"""
Stream Watchdog & Auto-Reconnect
Tracks last successful camera frame and computes reconnect backoff.

Used by StreamHandler. Does not open cameras itself.

Backoff uses EdgeAIConfig.RECONNECT_BACKOFF_SECONDS and is capped after
RECONNECT_RETRY_ATTEMPTS doubling steps. Retries continue indefinitely so a
dropped Wi-Fi/RTSP stream can recover without restarting the process.
"""

import time

from ..config import EdgeAIConfig
from ..utils.logger import log_debug, log_warning


# Consecutive failed reads before forcing a reconnect (even if capture still "open")
_FAIL_THRESHOLD = 8

# No successful frame for this many seconds → treat stream as dead
_STALE_SECONDS = 5.0


class ReconnectWatchdog:
    """
    Camera stream health tracker.

    Args:
        backoff_seconds: Base delay before first reconnect attempt.
        max_attempts:    Doubling steps before backoff is capped
                         (from EdgeAIConfig.RECONNECT_RETRY_ATTEMPTS).
        fail_threshold:  Failed cv2.read() calls before reconnect.
        stale_seconds:   Seconds without a good frame before reconnect.
    """

    def __init__(
        self,
        backoff_seconds: int = EdgeAIConfig.RECONNECT_BACKOFF_SECONDS,
        max_attempts: int = EdgeAIConfig.RECONNECT_RETRY_ATTEMPTS,
        fail_threshold: int = _FAIL_THRESHOLD,
        stale_seconds: float = _STALE_SECONDS,
    ):
        self.backoff_seconds = max(1, int(backoff_seconds))
        self.max_attempts = max(1, int(max_attempts))
        self.fail_threshold = max(1, int(fail_threshold))
        self.stale_seconds = float(stale_seconds)

        self._fail_count = 0
        self._reconnect_count = 0
        self._last_ok = time.time()
        self._last_reconnect_at = 0.0

    def record_success(self):
        """Call after a valid frame is read."""
        self._fail_count = 0
        self._last_ok = time.time()

    def record_failure(self):
        """Call after cv2.VideoCapture.read() fails or returns an empty frame."""
        self._fail_count += 1

    def is_stale(self) -> bool:
        """True if no successful frame arrived within stale_seconds."""
        return (time.time() - self._last_ok) >= self.stale_seconds

    def should_reconnect(self) -> bool:
        """True when the capture should be released and opened again."""
        return self._fail_count >= self.fail_threshold or self.is_stale()

    def next_backoff(self) -> float:
        """
        Exponential delay in seconds, capped after max_attempts steps.

        Example with backoff=5, max_attempts=3: 5s, 10s, 20s, 20s, ...
        """
        steps = min(max(self._reconnect_count, 0), self.max_attempts - 1)
        return float(self.backoff_seconds * (2 ** steps))

    def mark_reconnect_attempt(self):
        """Call immediately before opening the capture again."""
        self._reconnect_count += 1
        self._last_reconnect_at = time.time()
        log_warning(
            f"[Reconnect] Attempt #{self._reconnect_count} "
            f"(failures={self._fail_count}, stale={self.is_stale()})"
        )

    def wait_before_reconnect(self):
        """Sleep for next_backoff() seconds. Call before mark_reconnect_attempt()."""
        delay = self.next_backoff()
        log_debug(f"[Reconnect] Waiting {delay:.0f}s before reopen")
        time.sleep(delay)

    def reset_after_open(self):
        """Call after VideoCapture opens successfully (warmup still pending)."""
        self._fail_count = 0
        self._reconnect_count = 0
        self._last_ok = time.time()
        log_debug("[Reconnect] Capture opened — failure counters reset")

    @property
    def fail_count(self) -> int:
        return self._fail_count

    @property
    def reconnect_count(self) -> int:
        return self._reconnect_count

    @property
    def last_ok_age(self) -> float:
        """Seconds since last successful frame."""
        return time.time() - self._last_ok
