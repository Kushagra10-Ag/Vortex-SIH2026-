"""
Event Sender — Queued Async Event Batcher & Flush Loop
Buffers camera/footfall events in memory and sends them in batches.

Architecture:
  - enqueue(event) adds to thread-safe deque
  - A background daemon thread flushes every EVENT_FLUSH_INTERVAL_SECONDS
    OR whenever the queue reaches EVENT_BATCH_SIZE
  - On flush failure, events are re-queued (up to MAX_RETRY_BUFFER)
"""

import threading
import time
from collections import deque
from typing import Union, Optional

from .event_types import CameraEvent, FootfallEvent
from ..utils.logger import log_info, log_warning, log_error, log_debug
from ..config import EdgeAIConfig


# Maximum number of events to buffer before dropping oldest (prevent memory leak)
MAX_RETRY_BUFFER = 500


class EventSender:
    """
    Thread-safe event queue with timed flush to BIZmate backend.

    Args:
        backend_client: Initialized BackendClient instance.
        batch_size:     Number of events to batch before flushing.
        flush_interval: Seconds between automatic flushes.
    """

    def __init__(
        self,
        backend_client,  # BackendClient — imported lazily to avoid circular deps
        batch_size: int = EdgeAIConfig.EVENT_BATCH_SIZE,
        flush_interval: float = EdgeAIConfig.EVENT_FLUSH_INTERVAL_SECONDS,
    ):
        self._client = backend_client
        self._batch_size = batch_size
        self._flush_interval = flush_interval

        # Thread-safe FIFO queue for pending events
        self._queue: deque = deque(maxlen=MAX_RETRY_BUFFER)
        self._lock = threading.Lock()

        # Statistics
        self._total_sent = 0
        self._total_failed = 0
        self._total_dropped = 0

        # Background flush thread
        self._running = False
        self._thread: Optional[threading.Thread] = None

    # ─────────────────────────────────────────────────────────────────────────
    # PUBLIC API
    # ─────────────────────────────────────────────────────────────────────────

    def start(self):
        """Start background flush thread."""
        if self._running:
            log_warning("EventSender already running")
            return

        self._running = True
        self._thread = threading.Thread(
            target=self._flush_loop,
            name="event-sender-flush",
            daemon=True,   # Dies with main thread
        )
        self._thread.start()
        log_info(
            f"[EventSender] Started — batch_size={self._batch_size}, "
            f"flush_interval={self._flush_interval}s"
        )

    def stop(self):
        """Stop the flush loop and drain remaining events."""
        log_info("[EventSender] Stopping — flushing remaining events...")
        self._running = False
        if self._thread:
            self._thread.join(timeout=10)

        # Final drain
        self._flush_all()
        log_info(
            f"[EventSender] Stopped — sent={self._total_sent}, "
            f"failed={self._total_failed}, dropped={self._total_dropped}"
        )

    def enqueue(self, event: Union[CameraEvent, FootfallEvent]):
        """
        Add an event to the outbound queue.

        If queue is at max capacity (maxlen), oldest event is dropped automatically
        by the deque (Python deque behavior with maxlen).

        Args:
            event: CameraEvent or FootfallEvent to send.
        """
        with self._lock:
            self._queue.append(event)

        log_debug(
            f"[EventSender] Queued {getattr(event, 'event_type', type(event).__name__)} "
            f"(queue size: {len(self._queue)})"
        )

        # Eagerly flush if batch size reached
        if len(self._queue) >= self._batch_size:
            log_debug("[EventSender] Batch size reached — triggering early flush")
            self._flush_all()

    def queue_size(self) -> int:
        """Return current number of events waiting to be sent."""
        return len(self._queue)

    def stats(self) -> dict:
        """Return send statistics."""
        return {
            "total_sent": self._total_sent,
            "total_failed": self._total_failed,
            "total_dropped": self._total_dropped,
            "queue_size": self.queue_size(),
        }

    # ─────────────────────────────────────────────────────────────────────────
    # INTERNAL — FLUSH LOOP
    # ─────────────────────────────────────────────────────────────────────────

    def _flush_loop(self):
        """Background thread: flush queue every flush_interval seconds."""
        log_debug("[EventSender] Flush loop started")
        while self._running:
            time.sleep(self._flush_interval)
            if self._queue:
                self._flush_all()

    def _flush_all(self):
        """
        Drain entire queue and post each event to the backend.
        Events that fail are re-queued once (best-effort retry).
        """
        # Snapshot and drain the queue atomically
        with self._lock:
            events_to_send = list(self._queue)
            self._queue.clear()

        if not events_to_send:
            return

        log_debug(f"[EventSender] Flushing {len(events_to_send)} events...")

        retry_buffer = []
        for event in events_to_send:
            success = self._send_event(event)
            if not success:
                retry_buffer.append(event)

        # Re-queue failed events for next cycle
        if retry_buffer:
            with self._lock:
                for ev in retry_buffer:
                    self._queue.appendleft(ev)  # front of queue = priority
            log_warning(
                f"[EventSender] {len(retry_buffer)} events re-queued for retry"
            )

    def _send_event(self, event: Union[CameraEvent, FootfallEvent]) -> bool:
        """
        Route event to the correct backend endpoint.

        Args:
            event: Event object to send.

        Returns:
            True if sent successfully.
        """
        try:
            if isinstance(event, CameraEvent):
                success = self._client.post_camera_event(event)
            elif isinstance(event, FootfallEvent):
                success = self._client.post_footfall(event)
            else:
                log_warning(f"[EventSender] Unknown event type: {type(event)}")
                return True  # Don't retry unknown types

            if success:
                self._total_sent += 1
                log_debug(
                    f"[EventSender] Sent {getattr(event, 'event_type', type(event).__name__)}"
                )
            else:
                self._total_failed += 1
                log_warning(
                    f"[EventSender] Failed to send "
                    f"{getattr(event, 'event_type', type(event).__name__)}"
                )

            return success

        except Exception as e:
            self._total_failed += 1
            log_error(f"[EventSender] Exception sending event: {e}")
            return False

