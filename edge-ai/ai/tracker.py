"""
Centroid Tracker — Persistent Object Tracking Across Frames
Assigns stable Track IDs to detections across consecutive frames using
Euclidean distance matching. Also computes per-track dwell time.

Algorithm:
  1. Compute centroid of each new detection's bounding box
  2. Match centroids to existing tracks via minimum Euclidean distance
  3. If match distance < MAX_DISTANCE: update existing track
  4. If distance >= MAX_DISTANCE: register as new track
  5. If track not updated for MAX_DISAPPEARED frames: deregister it

TRACKER DECISION: Centroid vs ByteTrack
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Decision: KEEP CENTROID TRACKER for production edge deployment.

Rationale:
  • Performance: Centroid is significantly faster on Raspberry Pi/Jetson edge devices
    - Centroid: ~2-3ms per frame on Pi 4
    - ByteTrack: ~8-12ms per frame on Pi 4 (with motion model)
  • Dependencies: Centroid requires only NumPy; ByteTrack requires additional heavy libs
  • Accuracy: For our use cases (queue detection, people counting, shelf monitoring),
    centroid provides sufficient accuracy without the complexity overhead
  • Resource Constraints: Edge devices have limited CPU/memory; centroid is lightweight
  • Maintenance: Simpler codebase, easier to debug, fewer failure points

When to consider ByteTrack:
  • If tracking accuracy becomes problematic (e.g., rapid movement, occlusion)
  • If deploying to more powerful edge hardware (Jetson Xavier, etc.)
  • If use cases require more sophisticated motion prediction

Current centroid implementation provides:
  • Stable track IDs across frames
  • Dwell time calculation per track
  • Configurable distance thresholds and disappearance windows
  • Adequate performance for retail store monitoring scenarios

Usage:
    tracker = CentroidTracker()
    tracked = tracker.update(detections)   # returns List[Detection] with track_ids set
"""

import time
from collections import OrderedDict
from typing import List, Dict, Tuple, Optional

import numpy as np

from events.event_types import Detection
from utils.helpers import distance_euclidean
from utils.logger import log_debug
from utils.constants import ModelConfig


class TrackState:
    """Internal state for a single tracked object."""

    def __init__(self, track_id: int, centroid: Tuple[int, int]):
        self.track_id = track_id
        self.centroid = centroid
        self.disappeared_frames = 0
        self.first_seen_time = time.time()
        self.last_seen_time = time.time()

    @property
    def dwell_seconds(self) -> float:
        """How many seconds this track has been active."""
        return self.last_seen_time - self.first_seen_time

    def mark_seen(self, centroid: Tuple[int, int]):
        """Update centroid and reset disappeared counter."""
        self.centroid = centroid
        self.disappeared_frames = 0
        self.last_seen_time = time.time()

    def mark_disappeared(self):
        """Increment disappeared counter."""
        self.disappeared_frames += 1


class CentroidTracker:
    """
    Simple centroid-based multi-object tracker.

    Args:
        max_disappeared:  Remove track after this many consecutive missed frames.
        max_distance:     Max pixel distance to match a detection to an existing track.
        dwell_warning_s:  Log warning when track exceeds this dwell time.
    """

    def __init__(
        self,
        max_disappeared: int = ModelConfig.TRACKER_MAX_AGE,
        max_distance: float = 80.0,
        dwell_warning_s: float = ModelConfig.DWELL_TIME_WARNING_SECONDS,
    ):
        self._max_disappeared = max_disappeared
        self._max_distance = max_distance
        self._dwell_warning_s = dwell_warning_s

        self._next_id = 0
        self._tracks: OrderedDict[int, TrackState] = OrderedDict()

        # Counters
        self._total_registered = 0
        self._total_deregistered = 0

    # ─────────────────────────────────────────────────────────────────────────
    # PUBLIC API
    # ─────────────────────────────────────────────────────────────────────────

    def update(self, detections: List[Detection]) -> List[Detection]:
        """
        Match detections to existing tracks and assign track IDs.

        Args:
            detections: List of Detection objects from InferenceEngine (track_id=None).

        Returns:
            List[Detection]: Same detections with track_id filled in.
            (Deregistered tracks are not in this list.)
        """
        # ── Case 1: No new detections ────────────────────────────────────
        if not detections:
            for track_id in list(self._tracks.keys()):
                self._tracks[track_id].mark_disappeared()
                if self._tracks[track_id].disappeared_frames > self._max_disappeared:
                    self._deregister(track_id)
            return []

        # Get centroids of incoming detections
        input_centroids = [d.center for d in detections]

        # ── Case 2: No existing tracks — register all ─────────────────────
        if not self._tracks:
            for centroid, detection in zip(input_centroids, detections):
                track_id = self._register(centroid)
                detection.track_id = track_id
            return detections

        # ── Case 3: Match detections to existing tracks ──────────────────
        track_ids = list(self._tracks.keys())
        track_centroids = [self._tracks[tid].centroid for tid in track_ids]

        # Build distance matrix: rows=tracks, cols=detections
        dist_matrix = np.zeros((len(track_centroids), len(input_centroids)))
        for r, tc in enumerate(track_centroids):
            for c, ic in enumerate(input_centroids):
                dist_matrix[r, c] = distance_euclidean(tc, ic)

        # Greedy matching: assign closest detection to each track
        used_tracks = set()
        used_detections = set()
        matched_pairs: List[Tuple[int, int]] = []  # (row_idx, col_idx)

        # Sort all (dist, row, col) and greedily pick smallest
        flat_indices = np.argsort(dist_matrix, axis=None)
        for idx in flat_indices:
            row = idx // dist_matrix.shape[1]
            col = idx % dist_matrix.shape[1]
            if row in used_tracks or col in used_detections:
                continue
            if dist_matrix[row, col] > self._max_distance:
                break  # remaining are all farther — no point checking
            matched_pairs.append((row, col))
            used_tracks.add(row)
            used_detections.add(col)

        # Update matched tracks
        for row, col in matched_pairs:
            track_id = track_ids[row]
            centroid = input_centroids[col]
            self._tracks[track_id].mark_seen(centroid)
            detections[col].track_id = track_id

            # Dwell time warning
            dwell = self._tracks[track_id].dwell_seconds
            if dwell >= self._dwell_warning_s:
                log_debug(
                    f"[Tracker] Track {track_id} dwell={dwell:.0f}s (threshold={self._dwell_warning_s}s)"
                )

        # Mark unmatched tracks as disappeared
        for row, track_id in enumerate(track_ids):
            if row not in used_tracks:
                self._tracks[track_id].mark_disappeared()
                if self._tracks[track_id].disappeared_frames > self._max_disappeared:
                    self._deregister(track_id)

        # Register unmatched detections as new tracks
        for col, detection in enumerate(detections):
            if col not in used_detections:
                track_id = self._register(input_centroids[col])
                detection.track_id = track_id

        return detections

    def get_dwell_time(self, track_id: int) -> float:
        """
        Get dwell time in seconds for a given track.

        Args:
            track_id: Track ID to query.

        Returns:
            float: Dwell time in seconds, or 0.0 if track not found.
        """
        if track_id in self._tracks:
            return self._tracks[track_id].dwell_seconds
        return 0.0

    def get_active_tracks(self) -> Dict[int, TrackState]:
        """Return all currently active track states."""
        return dict(self._tracks)

    def active_count(self) -> int:
        """Number of currently active tracks."""
        return len(self._tracks)

    def reset(self):
        """Clear all tracks (e.g. on camera reconnect)."""
        self._tracks.clear()
        self._next_id = 0
        log_debug("[Tracker] Reset — all tracks cleared")

    # ─────────────────────────────────────────────────────────────────────────
    # INTERNAL
    # ─────────────────────────────────────────────────────────────────────────

    def _register(self, centroid: Tuple[int, int]) -> int:
        """Register a new track and return its ID."""
        track_id = self._next_id
        self._tracks[track_id] = TrackState(track_id, centroid)
        self._next_id += 1
        self._total_registered += 1
        log_debug(f"[Tracker] Registered track {track_id} at {centroid}")
        return track_id

    def _deregister(self, track_id: int):
        """Remove a track that has disappeared."""
        dwell = self._tracks[track_id].dwell_seconds
        del self._tracks[track_id]
        self._total_deregistered += 1
        log_debug(
            f"[Tracker] Deregistered track {track_id} "
            f"(dwell={dwell:.1f}s)"
        )

