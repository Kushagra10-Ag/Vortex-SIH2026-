"""
Queue Detector — Billing Counter Queue Length & Wait Time Analysis
Processes YOLO detections filtered to 'person' class within a billing counter ROI,
generates CameraEvents for:
  - QUEUE_OVERFLOW (when person count >= QUEUE_LENGTH_THRESHOLD)
  - QUEUE_EMPTY (when queue clears after being non-empty)

Also provides estimated wait time based on queue length.
"""

import time
from typing import List, Optional, Tuple

import numpy as np

from .inference import InferenceEngine, filter_persons
from .tracker import CentroidTracker
from ..events.event_builder import EventBuilder
from ..events.event_types import CameraEvent
from ..config import EdgeAIConfig
from ..utils.logger import log_debug, log_info, log_warning


class QueueDetector:
    """
    Detects and tracks people in a billing counter queue region.

    Generates:
      - QUEUE_OVERFLOW events when person count >= QUEUE_LENGTH_THRESHOLD
      - QUEUE_EMPTY events when queue clears after being non-empty

    Args:
        inference_engine:   Initialized InferenceEngine.
        tracker:            CentroidTracker for persistent IDs.
        event_builder:      EventBuilder instance.
        roi:                Billing counter ROI as [x, y, width, height] or None.
                           If None, uses full frame.
        queue_threshold:    Person count threshold for queue overflow alert.
                           Defaults to EdgeAIConfig.QUEUE_LENGTH_THRESHOLD (3).
        service_time_seconds: Average service time per person (for wait estimation).
    """

    def __init__(
        self,
        inference_engine: InferenceEngine,
        tracker: CentroidTracker,
        event_builder: EventBuilder,
        roi: Optional[List[int]] = None,
        queue_threshold: Optional[int] = None,
        service_time_seconds: float = 2.0,
    ):
        self._engine = inference_engine
        self._tracker = tracker
        self._builder = event_builder
        self._roi = roi
        self._queue_threshold = queue_threshold or EdgeAIConfig.QUEUE_LENGTH_THRESHOLD
        self._service_time = service_time_seconds

        # Track queue state for detecting transitions
        self._was_empty = True
        self._last_overflow_time = 0.0
        self._overflow_cooldown_seconds = 30.0  # Don't spam overflow alerts

        # Queue length history for wait time estimation
        self._queue_history: List[float] = []
        self._max_history_length = 10

        log_info(
            f"[QueueDetector] Initialized with threshold={self._queue_threshold}, "
            f"roi={self._roi}, service_time={self._service_time}s"
        )

    # ─────────────────────────────────────────────────────────────────────────
    # PUBLIC API
    # ─────────────────────────────────────────────────────────────────────────

    def process(
        self, frame: np.ndarray
    ) -> Tuple[List[CameraEvent], int, float]:
        """
        Process a single frame: detect people in ROI, track, and generate events.

        Args:
            frame: BGR numpy array from camera.

        Returns:
            Tuple[List[CameraEvent], int, float]:
                - List of events to enqueue (may be empty)
                - Current person count in queue ROI
                - Estimated wait time in seconds
        """
        events: List[CameraEvent] = []

        # 1. Run YOLO inference (with frame-skip)
        all_detections = self._engine.run(frame)

        # 2. Filter to persons only
        persons = filter_persons(all_detections)

        # 3. Filter persons to ROI if defined
        if self._roi is not None:
            persons = self._filter_to_roi(persons, self._roi)

        # 4. Update tracker with person detections in ROI
        tracked = self._tracker.update(persons)

        queue_count = len(tracked)

        # 5. Update queue history for wait time estimation
        self._update_queue_history(queue_count)

        # 6. Calculate estimated wait time
        wait_time = self._estimate_wait_time(queue_count)

        # 7. Emit QUEUE_OVERFLOW if threshold exceeded
        if queue_count >= self._queue_threshold:
            now = time.time()
            if now - self._last_overflow_time >= self._overflow_cooldown_seconds:
                self._last_overflow_time = now
                # Use combined ROI or largest person bbox as primary
                primary_bbox = self._roi if self._roi else (
                    max(tracked, key=lambda d: (d.bbox[2] * d.bbox[3]) if d.bbox else 0).bbox
                    if tracked else None
                )
                events.append(
                    self._builder.queue_overflow(
                        count=queue_count,
                        bbox=primary_bbox,
                        confidence=self._get_average_confidence(tracked),
                        frame=frame,
                    )
                )
                log_warning(
                    f"[QueueDetector] QUEUE_OVERFLOW: count={queue_count}, "
                    f"threshold={self._queue_threshold}, est_wait={wait_time:.1f}s"
                )

        # 8. Emit QUEUE_EMPTY when queue clears after being non-empty
        if queue_count == 0 and not self._was_empty:
            self._was_empty = True
            events.append(
                self._builder.queue_empty(frame=frame)
            )
            log_info("[QueueDetector] QUEUE_EMPTY: queue has cleared")

        # Update empty state tracker
        if queue_count > 0:
            self._was_empty = False

        return events, queue_count, wait_time

    def set_roi(self, roi: List[int]):
        """
        Update the billing counter ROI.

        Args:
            roi: [x, y, width, height] in pixels
        """
        self._roi = roi
        log_info(f"[QueueDetector] ROI updated to {roi}")

    def get_roi(self) -> Optional[List[int]]:
        """Return current ROI or None if using full frame."""
        return self._roi

    def get_queue_history(self) -> List[float]:
        """Return recent queue length history."""
        return self._queue_history.copy()

    # ─────────────────────────────────────────────────────────────────────────
    # INTERNAL
    # ─────────────────────────────────────────────────────────────────────────

    def _filter_to_roi(self, detections: List, roi: List[int]) -> List:
        """
        Filter detections to those whose center point is within the ROI.

        Args:
            detections: List of Detection objects
            roi: [x, y, width, height]

        Returns:
            Filtered list of detections
        """
        rx, ry, rw, rh = roi
        rx2, ry2 = rx + rw, ry + rh

        filtered = []
        for det in detections:
            if det.center:
                cx, cy = det.center
                if rx <= cx <= rx2 and ry <= cy <= ry2:
                    filtered.append(det)
                    log_debug(
                        f"[QueueDetector] Person in ROI: center=({cx}, {cy}), "
                        f"roi=({rx}, {ry}, {rw}, {rh})"
                    )

        return filtered

    def _update_queue_history(self, count: int):
        """Update queue length history with current count."""
        self._queue_history.append(float(count))
        if len(self._queue_history) > self._max_history_length:
            self._queue_history.pop(0)

    def _estimate_wait_time(self, current_count: int) -> float:
        """
        Estimate wait time based on queue length.

        Simple model: wait_time = queue_count * service_time

        Can be enhanced with:
        - Historical average service time
        - Time of day adjustments
        - Moving average of recent queue lengths

        Args:
            current_count: Current number of people in queue

        Returns:
            Estimated wait time in seconds
        """
        if current_count == 0:
            return 0.0

        # Basic estimation
        base_wait = current_count * self._service_time

        # If we have history, use average for slightly smoother estimation
        if self._queue_history:
            avg_queue = sum(self._queue_history) / len(self._queue_history)
            # Blend current count with historical average (70% current, 30% historical)
            blended_count = (current_count * 0.7) + (avg_queue * 0.3)
            base_wait = blended_count * self._service_time

        return max(0.0, base_wait)

    def _get_average_confidence(self, detections: List) -> float:
        """Calculate average confidence of tracked detections."""
        if not detections:
            return 0.0
        confidences = [d.confidence for d in detections if d.confidence is not None]
        if not confidences:
            return 0.0
        return sum(confidences) / len(confidences)
