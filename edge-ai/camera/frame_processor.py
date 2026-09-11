"""
Frame Processor — Resize, color-space, and normalize camera frames
Delegates to utils.image_utils (no duplicate OpenCV logic).

YOLO inference (ai/inference.py) accepts BGR numpy frames from OpenCV.
process() therefore keeps BGR and only resizes to EdgeAIConfig camera size.
"""

from typing import Optional

import numpy as np

from ..config import EdgeAIConfig
from ..utils.image_utils import (
    bgr_to_grayscale,
    bgr_to_rgb,
    get_frame_dimensions,
    normalize_frame,
    resize_frame,
)
from ..utils.logger import log_debug, log_warning


class FrameProcessor:
    """
    Prepares raw capture frames for inference and optional preview.

    Args:
        width:           Target width (EdgeAIConfig.CAMERA_WIDTH).
        height:          Target height (EdgeAIConfig.CAMERA_HEIGHT).
        maintain_aspect: If True, letterbox via resize_frame (no stretch).
    """

    def __init__(
        self,
        width: int = EdgeAIConfig.CAMERA_WIDTH,
        height: int = EdgeAIConfig.CAMERA_HEIGHT,
        maintain_aspect: bool = True,
    ):
        self.width = int(width)
        self.height = int(height)
        self.maintain_aspect = maintain_aspect

    def process(self, frame: Optional[np.ndarray]) -> Optional[np.ndarray]:
        """
        Resize a BGR frame to the configured camera size.

        Returns:
            BGR numpy array, or None if the input is empty.
        """
        if frame is None or getattr(frame, "size", 0) == 0:
            log_warning("[FrameProcessor] Empty frame — skip")
            return None

        h, w, _c = get_frame_dimensions(frame)
        if w == self.width and h == self.height:
            return frame

        resized = resize_frame(
            frame,
            self.width,
            self.height,
            maintain_aspect=self.maintain_aspect,
        )
        log_debug(
            f"[FrameProcessor] Resized {w}x{h} -> {self.width}x{self.height}"
        )
        return resized

    def to_rgb(self, frame: Optional[np.ndarray]) -> Optional[np.ndarray]:
        """BGR → RGB. Used for preview/PIL, not for ultralytics predict()."""
        if frame is None or getattr(frame, "size", 0) == 0:
            return None
        return bgr_to_rgb(frame)

    def to_gray(self, frame: Optional[np.ndarray]) -> Optional[np.ndarray]:
        """BGR → grayscale."""
        if frame is None or getattr(frame, "size", 0) == 0:
            return None
        return bgr_to_grayscale(frame)

    def to_normalized(
        self,
        frame: Optional[np.ndarray],
        to_01: bool = True,
    ) -> Optional[np.ndarray]:
        """
        Float32 normalize. Not required for ultralytics YOLO (it normalizes
        internally); kept because plan.md lists color/normalize as a step.
        """
        if frame is None or getattr(frame, "size", 0) == 0:
            return None
        return normalize_frame(frame, normalize_to_01=to_01)
