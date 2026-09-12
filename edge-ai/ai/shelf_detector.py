"""
Shelf Detector — Smart Shelf Stock Level & Out-of-Stock Detection
Processes YOLO detections within configured shelf ROIs to estimate fill percentage,
generates CameraEvents for:
  - OUT_OF_STOCK_DETECTED (when fill % falls below threshold)

Also provides per-shelf fill percentage and stock status.
"""

from typing import List, Optional, Dict, Tuple
import time

import numpy as np

from .inference import InferenceEngine
from events.event_builder import EventBuilder
from events.event_types import CameraEvent
from utils.constants import ModelConfig, ShelfStockStatus
from utils.logger import log_debug, log_info, log_warning


class ShelfConfig:
    """
    Configuration for a single shelf monitoring zone.

    Args:
        shelf_id:           Unique identifier for this shelf (e.g., 'A1', 'B2')
        roi:                Region of interest [x, y, width, height] in pixels
        product_classes:    List of COCO class IDs to count as products on this shelf
                           (e.g., [39 for bottle, 41 for cup, etc.)
        expected_capacity:  Expected number of product slots when fully stocked
        low_stock_threshold: Fill % below this is considered 'low_stock' (default 30%)
        empty_threshold:    Fill % below this is considered 'empty' (default 10%)
    """

    def __init__(
        self,
        shelf_id: str,
        roi: List[int],
        product_classes: Optional[List[int]] = None,
        expected_capacity: int = 10,
        low_stock_threshold: float = 30.0,
        empty_threshold: float = 10.0,
    ):
        self.shelf_id = shelf_id
        self.roi = roi
        self.product_classes = product_classes or []  # Empty = count all objects
        self.expected_capacity = max(1, expected_capacity)
        self.low_stock_threshold = low_stock_threshold
        self.empty_threshold = empty_threshold

    def to_dict(self) -> dict:
        """Export shelf configuration as dictionary."""
        return {
            "shelf_id": self.shelf_id,
            "roi": self.roi,
            "product_classes": self.product_classes,
            "expected_capacity": self.expected_capacity,
            "low_stock_threshold": self.low_stock_threshold,
            "empty_threshold": self.empty_threshold,
        }


class ShelfDetector:
    """
    Detects stock levels on configured shelf regions.

    Generates:
      - OUT_OF_STOCK_DETECTED events when shelf fill % is below threshold

    Args:
        inference_engine:   Initialized InferenceEngine.
        event_builder:      EventBuilder instance.
        shelf_configs:      List of ShelfConfig objects defining shelves to monitor.
        out_of_stock_threshold: Fill % below this triggers out_of-stock alert.
                               Defaults to ModelConfig.SHELF_EMPTY_PERCENTAGE (10%).
    """

    def __init__(
        self,
        inference_engine: InferenceEngine,
        event_builder: EventBuilder,
        shelf_configs: Optional[List[ShelfConfig]] = None,
        out_of_stock_threshold: Optional[float] = None,
    ):
        self._engine = inference_engine
        self._builder = event_builder
        self._shelf_configs = shelf_configs or []
        self._out_of_stock_threshold = out_of_stock_threshold or ModelConfig.SHELF_EMPTY_PERCENTAGE

        # Track last alert time per shelf to prevent spamming
        self._last_alert_time: Dict[str, float] = {}
        self._alert_cooldown_seconds = 60.0  # Don't alert same shelf more than once per minute

        # Store current shelf states
        self._shelf_states: Dict[str, dict] = {}

        log_info(
            f"[ShelfDetector] Initialized with {len(self._shelf_configs)} shelves, "
            f"out_of_stock_threshold={self._out_of_stock_threshold}%"
        )

    # ─────────────────────────────────────────────────────────────────────────
    # PUBLIC API
    # ─────────────────────────────────────────────────────────────────────────

    def process(self, frame: np.ndarray, detections=None) -> Tuple[List[CameraEvent], Dict[str, dict]]:
        """
        Process a single frame: detect products in shelf ROIs and generate events.

        Args:
            frame: BGR numpy array from camera.

        Returns:
            Tuple[List[CameraEvent], Dict[str, dict]]:
                - List of events to enqueue (may be empty)
                - Dictionary mapping shelf_id to current state (fill%, status, etc.)
        """
        events: List[CameraEvent] = []
        shelf_states = {}

        # Reuse shared frame inference when supplied by the daemon.
        all_detections = detections if detections is not None else self._engine.run(frame)

        # Process each shelf configuration
        for shelf_config in self._shelf_configs:
            shelf_id = shelf_config.shelf_id

            # Filter detections to this shelf's ROI and product classes
            shelf_detections = self._filter_to_shelf(
                all_detections, shelf_config.roi, shelf_config.product_classes
            )

            # Calculate fill percentage
            fill_percentage = self._calculate_fill_percentage(
                len(shelf_detections), shelf_config.expected_capacity
            )

            # Determine stock status
            status = self._determine_status(fill_percentage, shelf_config)

            # Store shelf state
            state = {
                "shelf_id": shelf_id,
                "roi": shelf_config.roi,
                "product_count": len(shelf_detections),
                "expected_capacity": shelf_config.expected_capacity,
                "fill_percentage": fill_percentage,
                "status": status,
                "timestamp": time.time(),
            }
            shelf_states[shelf_id] = state
            self._shelf_states[shelf_id] = state

            # Emit OUT_OF_STOCK_DETECTED if below threshold
            if fill_percentage <= self._out_of_stock_threshold:
                if self._should_alert(shelf_id):
                    events.append(
                        self._builder.out_of_stock(
                            fill_percentage=fill_percentage,
                            shelf_zone_id=shelf_id,
                            frame=frame,
                        )
                    )
                    log_warning(
                        f"[ShelfDetector] OUT_OF_STOCK_DETECTED: shelf={shelf_id}, "
                        f"fill={fill_percentage:.1f}%, count={len(shelf_detections)}/{shelf_config.expected_capacity}"
                    )

        return events, shelf_states

    def add_shelf(self, shelf_config: ShelfConfig):
        """Add a new shelf configuration."""
        self._shelf_configs.append(shelf_config)
        log_info(f"[ShelfDetector] Added shelf: {shelf_config.shelf_id}")

    def remove_shelf(self, shelf_id: str):
        """Remove a shelf configuration by ID."""
        self._shelf_configs = [s for s in self._shelf_configs if s.shelf_id != shelf_id]
        if shelf_id in self._shelf_states:
            del self._shelf_states[shelf_id]
        log_info(f"[ShelfDetector] Removed shelf: {shelf_id}")

    def get_shelf_state(self, shelf_id: str) -> Optional[dict]:
        """Get current state for a specific shelf."""
        return self._shelf_states.get(shelf_id)

    def get_all_shelf_states(self) -> Dict[str, dict]:
        """Get current states for all shelves."""
        return self._shelf_states.copy()

    def get_shelf_configs(self) -> List[ShelfConfig]:
        """Return list of shelf configurations."""
        return self._shelf_configs.copy()

    # ─────────────────────────────────────────────────────────────────────────
    # INTERNAL
    # ─────────────────────────────────────────────────────────────────────────

    def _filter_to_shelf(
        self, detections: List, roi: List[int], product_classes: List[int]
    ) -> List:
        """
        Filter detections to those within shelf ROI and matching product classes.

        Args:
            detections: List of Detection objects
            roi: [x, y, width, height]
            product_classes: List of class IDs to count (empty = all)

        Returns:
            Filtered list of detections
        """
        rx, ry, rw, rh = roi
        rx2, ry2 = rx + rw, ry + rh

        filtered = []
        for det in detections:
            # Check if detection center is within ROI
            if det.center:
                cx, cy = det.center
                if not (rx <= cx <= rx2 and ry <= cy <= ry2):
                    continue

            # Check if class matches product classes (if specified)
            if product_classes and det.class_id not in product_classes:
                continue

            filtered.append(det)
            log_debug(
                f"[ShelfDetector] Product in shelf {roi}: "
                f"class={det.class_name}, center={det.center}"
            )

        return filtered

    def _calculate_fill_percentage(self, count: int, capacity: int) -> float:
        """
        Calculate fill percentage based on detected count vs expected capacity.

        Args:
            count: Number of products detected
            capacity: Expected capacity when fully stocked

        Returns:
            Fill percentage (0.0 to 100.0)
        """
        if capacity <= 0:
            return 0.0
        fill = (count / capacity) * 100.0
        return min(100.0, max(0.0, fill))

    def _determine_status(self, fill_percentage: float, shelf_config: ShelfConfig) -> str:
        """
        Determine shelf stock status based on fill percentage.

        Args:
            fill_percentage: Current fill percentage
            shelf_config: Shelf configuration with thresholds

        Returns:
            Status string: 'normal', 'low_stock', or 'empty'
        """
        if fill_percentage <= shelf_config.empty_threshold:
            return ShelfStockStatus.EMPTY
        elif fill_percentage <= shelf_config.low_stock_threshold:
            return ShelfStockStatus.LOW_STOCK
        else:
            return ShelfStockStatus.NORMAL

    def _should_alert(self, shelf_id: str) -> bool:
        """
        Check if we should send an alert for this shelf (cooldown check).

        Args:
            shelf_id: Shelf identifier

        Returns:
            True if alert should be sent, False if in cooldown
        """
        now = time.time()
        last_alert = self._last_alert_time.get(shelf_id, 0.0)
        if now - last_alert >= self._alert_cooldown_seconds:
            self._last_alert_time[shelf_id] = now
            return True
        return False


# ─────────────────────────────────────────────────────────────────────────
# PRESET SHELF CONFIGURATIONS
# ─────────────────────────────────────────────────────────────────────────

def create_default_shelf_configs(roi_overrides: Optional[Dict[str, List[int]]] = None) -> List[ShelfConfig]:
    """
    Create a set of default shelf configurations for common retail scenarios.

    Returns:
        List of ShelfConfig objects for typical kirana store layout
    """
    configs = [
        # Shelf A1 - Beverages (left side of frame)
        ShelfConfig(
            shelf_id="A1",
            roi=[50, 200, 300, 150],
            product_classes=[39, 41],  # bottle, cup
            expected_capacity=12,
            low_stock_threshold=30.0,
            empty_threshold=10.0,
        ),
        # Shelf A2 - Snacks (center-left)
        ShelfConfig(
            shelf_id="A2",
            roi=[370, 200, 300, 150],
            product_classes=[46, 47],  # banana, apple (food items)
            expected_capacity=10,
            low_stock_threshold=30.0,
            empty_threshold=10.0,
        ),
        # Shelf B1 - Personal Care (center-right)
        ShelfConfig(
            shelf_id="B1",
            roi=[690, 200, 300, 150],
            product_classes=[67, 72],  # cell phone, toothbrush (general objects)
            expected_capacity=8,
            low_stock_threshold=30.0,
            empty_threshold=10.0,
        ),
        # Shelf B2 - General (right side)
        ShelfConfig(
            shelf_id="B2",
            roi=[1010, 200, 250, 150],
            product_classes=[],  # Count all objects
            expected_capacity=15,
            low_stock_threshold=30.0,
            empty_threshold=10.0,
        ),
    ]
    for shelf_config in configs:
        if roi_overrides and shelf_config.shelf_id in roi_overrides:
            shelf_config.roi = roi_overrides[shelf_config.shelf_id]
    return configs
