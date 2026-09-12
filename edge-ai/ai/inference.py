"""
Inference Engine — Run YOLO Predictions on Camera Frames
Wraps ultralytics YOLO .predict() with frame-skip logic, confidence filtering,
and structured Detection output.

Frame-skip:  Only run YOLO every INFERENCE_SKIP_FRAMES frames.
             In between, return the last cached result.
             This dramatically reduces CPU load (e.g. 30fps camera → 10 inferences/s).

Usage:
    engine = InferenceEngine(model)
    detections = engine.run(frame)   # returns List[Detection]
"""

from typing import List, Optional
import numpy as np

from .model_loader import ModelLoader
from events.event_types import Detection
from utils.helpers import bounding_box_center
from utils.logger import log_debug, log_warning, log_error
from config import EdgeAIConfig


# COCO class ID for 'person'
_PERSON_CLASS_ID = 0


class InferenceEngine:
    """
    Runs YOLO object detection on video frames with frame-skip optimization.

    Args:
        model_loader:       Initialized ModelLoader with model already loaded.
        confidence:         Minimum confidence to accept a detection.
        iou:                IoU threshold for non-maximum suppression.
        skip_frames:        Run inference every N frames; cache result between.
        target_classes:     If set, only return detections for these class IDs.
                            None = return all classes.
    """

    def __init__(
        self,
        model_loader: ModelLoader,
        confidence: float = EdgeAIConfig.MODEL_CONFIDENCE_THRESHOLD,
        iou: float = EdgeAIConfig.MODEL_IOU_THRESHOLD,
        skip_frames: int = EdgeAIConfig.INFERENCE_SKIP_FRAMES,
        target_classes: Optional[List[int]] = None,
    ):
        if not model_loader.is_loaded():
            raise ValueError("[InferenceEngine] ModelLoader must have model loaded before use")

        self._model = model_loader.model
        self._class_names = model_loader.class_names
        self._confidence = confidence
        self._iou = iou
        self._skip_frames = max(1, skip_frames)
        self._target_classes = target_classes

        # Frame-skip state
        self._frame_counter = 0
        self._last_detections: List[Detection] = []

        # Statistics
        self._total_frames = 0
        self._total_inferences = 0

        log_debug(
            f"[InferenceEngine] Ready — "
            f"conf={confidence}, iou={iou}, skip_frames={skip_frames}"
        )

    # ─────────────────────────────────────────────────────────────────────────
    # PUBLIC API
    # ─────────────────────────────────────────────────────────────────────────

    def run(self, frame: np.ndarray) -> List[Detection]:
        """
        Run inference on a camera frame.

        Returns cached result on skipped frames for performance.

        Args:
            frame: BGR numpy array from OpenCV VideoCapture.

        Returns:
            List[Detection]: All detections above confidence threshold.
        """
        if frame is None or frame.size == 0:
            return []

        self._total_frames += 1
        self._frame_counter += 1

        # Only infer on every Nth frame
        if self._frame_counter < self._skip_frames:
            return self._last_detections  # return cached

        # Reset skip counter and run inference
        self._frame_counter = 0
        self._total_inferences += 1

        try:
            detections = self._predict(frame)
            self._last_detections = detections
            log_debug(
                f"[InferenceEngine] Frame #{self._total_frames}: "
                f"{len(detections)} detections "
                f"(inference #{self._total_inferences})"
            )
            return detections

        except Exception as e:
            log_error(f"[InferenceEngine] Prediction error: {e}")
            return self._last_detections  # return stale cache on error

    def run_forced(self, frame: np.ndarray) -> List[Detection]:
        """
        Run inference on this frame regardless of frame-skip counter.
        Use for manual snapshot requests or critical events.
        """
        self._frame_counter = 0
        return self.run(frame)

    @property
    def last_detections(self) -> List[Detection]:
        """Return the most recent detection list."""
        return self._last_detections

    def stats(self) -> dict:
        """Return inference performance statistics."""
        return {
            "total_frames": self._total_frames,
            "total_inferences": self._total_inferences,
            "inference_rate": (
                self._total_inferences / self._total_frames
                if self._total_frames > 0 else 0
            ),
        }

    # ─────────────────────────────────────────────────────────────────────────
    # INTERNAL
    # ─────────────────────────────────────────────────────────────────────────

    def _predict(self, frame: np.ndarray) -> List[Detection]:
        """
        Call YOLO model and parse results into Detection objects.

        Args:
            frame: BGR numpy frame.

        Returns:
            List[Detection]: Filtered, structured detections.
        """
        # ultralytics predict() accepts numpy BGR frames directly
        results = self._model.predict(
            source=frame,
            conf=self._confidence,
            iou=self._iou,
            verbose=False,   # suppress per-frame console spam
            stream=False,
        )

        detections: List[Detection] = []

        for result in results:
            if result.boxes is None:
                continue

            boxes = result.boxes
            for i in range(len(boxes)):
                try:
                    # Class ID and name
                    class_id = int(boxes.cls[i].item())
                    confidence = float(boxes.conf[i].item())

                    # Skip if class filter set and this class not in it
                    if (
                        self._target_classes is not None
                        and class_id not in self._target_classes
                    ):
                        continue

                    # Class name (use loaded names or ultralytics built-in)
                    if self._class_names and class_id < len(self._class_names):
                        class_name = self._class_names[class_id]
                    elif result.names and class_id in result.names:
                        class_name = result.names[class_id]
                    else:
                        class_name = f"class_{class_id}"

                    # Bounding box: ultralytics returns [x1, y1, x2, y2]
                    # Convert to [x, y, w, h] format (top-left + size)
                    x1, y1, x2, y2 = boxes.xyxy[i].tolist()
                    x = int(x1)
                    y = int(y1)
                    w = int(x2 - x1)
                    h = int(y2 - y1)
                    bbox = [x, y, w, h]
                    center = bounding_box_center(bbox)

                    detections.append(Detection(
                        class_id=class_id,
                        class_name=class_name,
                        confidence=round(confidence, 4),
                        bbox=bbox,
                        center=center,
                        track_id=None,  # assigned by tracker later
                    ))

                except Exception as e:
                    log_warning(f"[InferenceEngine] Error parsing detection {i}: {e}")
                    continue

        return detections


def filter_persons(detections: List[Detection]) -> List[Detection]:
    """Utility: filter detections to only person class (COCO id=0)."""
    return [d for d in detections if d.class_id == _PERSON_CLASS_ID]


def highest_confidence(detections: List[Detection]) -> Optional[Detection]:
    """Utility: return the detection with highest confidence score."""
    if not detections:
        return None
    return max(detections, key=lambda d: d.confidence)

