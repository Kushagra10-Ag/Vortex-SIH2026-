"""
People Detector — Person Count, Footfall & Dwell Time Events
Processes YOLO detections filtered to 'person' class, updates the tracker,
and generates CameraEvents for:
  - PERSON_DETECTED (periodic, when people are in frame)
  - DWELL_TIME_HIGH (when someone lingers too long)

Also tracks entry/exit deltas for the footfall counter.
"""

import time
from typing import List, Optional, Tuple

import numpy as np

from .inference import InferenceEngine, filter_persons
from .tracker import CentroidTracker
from events.event_builder import EventBuilder
from events.event_types import CameraEvent
from utils.constants import ModelConfig
from utils.logger import log_debug, log_info


class PeopleDetector:
    """
    Detects and tracks people in video frames.

    Generates:
      - PERSON_DETECTED events when at least one person is in frame
      - DWELL_TIME_HIGH events when a tracked person exceeds the dwell threshold

    Args:
        inference_engine:   Initialized InferenceEngine.
        tracker:            CentroidTracker for persistent IDs.
        event_builder:      EventBuilder instance.
        person_event_interval_s: Minimum seconds between PERSON_DETECTED events
                                 (avoids flooding the backend with every frame).
        dwell_threshold_s:  Seconds before triggering DWELL_TIME_HIGH.
    """

    def __init__(
        self,
        inference_engine: InferenceEngine,
        tracker: CentroidTracker,
        event_builder: EventBuilder,
        person_event_interval_s: float = 5.0,
        dwell_threshold_s: float = ModelConfig.DWELL_TIME_WARNING_SECONDS,
    ):
        self._engine = inference_engine
        self._tracker = tracker
        self._builder = event_builder
        self._person_event_interval = person_event_interval_s
        self._dwell_threshold = dwell_threshold_s

        # Throttle: last time we emitted a PERSON_DETECTED event
        self._last_person_event_time = 0.0

        # Track which track_ids we've already fired DWELL_TIME_HIGH for
        # (reset when track is lost)
        self._dwell_alerted: set = set()

        # Footfall state
        self._prev_count = 0
        self._entry_delta = 0
        self._exit_delta = 0

    # ─────────────────────────────────────────────────────────────────────────
    # PUBLIC API
    # ─────────────────────────────────────────────────────────────────────────

    def process(
        self, frame: np.ndarray, detections=None
    ) -> Tuple[List[CameraEvent], int]:
        """
        Process a single frame: detect, track, and generate events.

        Args:
            frame: BGR numpy array from camera.

        Returns:
            Tuple[List[CameraEvent], int]:
                - List of events to enqueue (may be empty)
                - Current person count in frame
        """
        events: List[CameraEvent] = []

        # 1. Reuse shared frame inference when supplied by the daemon.
        all_detections = detections if detections is not None else self._engine.run(frame)

        # 2. Filter to persons only
        persons = filter_persons(all_detections)

        # 3. Update tracker with person detections
        tracked = self._tracker.update(persons)

        person_count = len(tracked)

        # 4. Track footfall deltas
        self._update_footfall(person_count)

        # 5. Emit PERSON_DETECTED (throttled)
        if person_count > 0:
            now = time.time()
            if now - self._last_person_event_time >= self._person_event_interval:
                self._last_person_event_time = now
                # Use largest person detection as primary bbox
                primary = max(tracked, key=lambda d: (d.bbox[2] * d.bbox[3]) if d.bbox else 0)
                events.append(
                    self._builder.person_detected(
                        count=person_count,
                        bbox=primary.bbox,
                        confidence=primary.confidence,
                        frame=frame,
                    )
                )
                log_debug(
                    f"[PeopleDetector] PERSON_DETECTED: count={person_count}"
                )

        # 6. Emit DWELL_TIME_HIGH for long-dwelling tracks
        for detection in tracked:
            tid = detection.track_id
            if tid is None:
                continue
            dwell = self._tracker.get_dwell_time(tid)
            if dwell >= self._dwell_threshold and tid not in self._dwell_alerted:
                self._dwell_alerted.add(tid)
                events.append(
                    self._builder.dwell_time_high(
                        track_id=tid,
                        dwell_seconds=dwell,
                        bbox=detection.bbox,
                        frame=frame,
                    )
                )
                log_info(
                    f"[PeopleDetector] DWELL_TIME_HIGH: "
                    f"track={tid}, dwell={dwell:.1f}s"
                )

        # 7. Clean up dwell alerts for lost tracks
        active_ids = {d.track_id for d in tracked if d.track_id is not None}
        self._dwell_alerted = self._dwell_alerted & active_ids

        return events, person_count

    def get_footfall_delta(self) -> Tuple[int, int]:
        """
        Return and reset footfall entry/exit deltas since last call.

        Returns:
            Tuple[int, int]: (entry_delta, exit_delta)
        """
        entry = self._entry_delta
        exit_ = self._exit_delta
        self._entry_delta = 0
        self._exit_delta = 0
        return entry, exit_

    # ─────────────────────────────────────────────────────────────────────────
    # INTERNAL
    # ─────────────────────────────────────────────────────────────────────────

    def _update_footfall(self, current_count: int):
        """Track entry/exit deltas based on person count changes."""
        delta = current_count - self._prev_count
        if delta > 0:
            self._entry_delta += delta
        elif delta < 0:
            self._exit_delta += abs(delta)
        self._prev_count = current_count

