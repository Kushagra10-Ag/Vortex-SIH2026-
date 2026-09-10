"""
Model Loader — Load YOLOv11 Weights via Ultralytics API
Loads the YOLO model from the weights/ directory and prepares it for inference.

Supports:
  - YOLOv11 (weights/yolov11.pt) — primary model
  - CPU or CUDA GPU inference via config.ENABLE_GPU
  - Graceful failure with clear error messages

Usage:
    loader = ModelLoader()
    model = loader.load()
"""

import os
from typing import Optional

from ..utils.logger import log_info, log_warning, log_error
from ..config import EdgeAIConfig


# Default weights path relative to edge-ai root
_DEFAULT_WEIGHTS = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "weights", "yolov11.pt"
)

# COCO names file
_DEFAULT_NAMES = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "weights", "coco.names"
)


class ModelLoader:
    """
    Loads and configures a YOLO model for edge inference.

    Args:
        weights_path:  Path to .pt weights file. Defaults to weights/yolov11.pt.
        use_gpu:       Use CUDA GPU if True (requires CUDA build of PyTorch).
        confidence:    Default confidence threshold for predictions.
        iou:           Default IoU threshold for NMS.
    """

    def __init__(
        self,
        weights_path: str = _DEFAULT_WEIGHTS,
        use_gpu: bool = EdgeAIConfig.ENABLE_GPU,
        confidence: float = EdgeAIConfig.MODEL_CONFIDENCE_THRESHOLD,
        iou: float = EdgeAIConfig.MODEL_IOU_THRESHOLD,
    ):
        self.weights_path = weights_path
        self.use_gpu = use_gpu
        self.confidence = confidence
        self.iou = iou

        self._model = None
        self._class_names: list = []
        self._device: str = "cpu"

    # ─────────────────────────────────────────────────────────────────────────
    # PUBLIC API
    # ─────────────────────────────────────────────────────────────────────────

    def load(self):
        """
        Load YOLO model from weights file.

        Returns:
            ultralytics.YOLO: Loaded model ready for .predict() calls.

        Raises:
            RuntimeError: If model file not found or ultralytics not installed.
        """
        if self._model is not None:
            log_warning("[ModelLoader] Model already loaded — returning cached instance")
            return self._model

        self._validate_weights_file()
        self._determine_device()
        self._load_class_names()
        self._load_model()

        return self._model

    @property
    def model(self):
        """Return loaded model (None if not yet loaded)."""
        return self._model

    @property
    def class_names(self) -> list:
        """Return list of COCO class name strings."""
        return self._class_names

    @property
    def device(self) -> str:
        """Return active compute device ('cpu' or 'cuda:0')."""
        return self._device

    def is_loaded(self) -> bool:
        """True if model has been loaded successfully."""
        return self._model is not None

    # ─────────────────────────────────────────────────────────────────────────
    # INTERNAL
    # ─────────────────────────────────────────────────────────────────────────

    def _validate_weights_file(self):
        """Check that weights file exists and is readable."""
        if not os.path.isfile(self.weights_path):
            raise RuntimeError(
                f"[ModelLoader] Weights file not found: {self.weights_path}\n"
                f"Expected: weights/yolov11.pt in edge-ai directory"
            )
        size_mb = os.path.getsize(self.weights_path) / (1024 * 1024)
        log_info(
            f"[ModelLoader] Found weights: {self.weights_path} ({size_mb:.1f} MB)"
        )

    def _determine_device(self):
        """Determine compute device (CUDA vs CPU)."""
        if self.use_gpu:
            try:
                import torch
                if torch.cuda.is_available():
                    self._device = "cuda:0"
                    log_info(
                        f"[ModelLoader] GPU detected: {torch.cuda.get_device_name(0)}"
                    )
                else:
                    log_warning(
                        "[ModelLoader] ENABLE_GPU=true but CUDA not available — using CPU"
                    )
                    self._device = "cpu"
            except ImportError:
                log_warning("[ModelLoader] PyTorch not found — using CPU")
                self._device = "cpu"
        else:
            self._device = "cpu"

        log_info(f"[ModelLoader] Compute device: {self._device}")

    def _load_class_names(self):
        """Load COCO class names from coco.names file."""
        if os.path.isfile(_DEFAULT_NAMES):
            try:
                with open(_DEFAULT_NAMES, "r") as f:
                    self._class_names = [line.strip() for line in f if line.strip()]
                log_info(
                    f"[ModelLoader] Loaded {len(self._class_names)} class names "
                    f"from {_DEFAULT_NAMES}"
                )
            except Exception as e:
                log_warning(f"[ModelLoader] Could not read coco.names: {e}")
                self._class_names = []
        else:
            log_warning(f"[ModelLoader] coco.names not found at {_DEFAULT_NAMES}")
            self._class_names = []

    def _load_model(self):
        """Import ultralytics and load YOLO model."""
        try:
            from ultralytics import YOLO
        except ImportError:
            raise RuntimeError(
                "[ModelLoader] 'ultralytics' package not installed.\n"
                "Install with: pip install ultralytics"
            )

        log_info(f"[ModelLoader] Loading YOLO model from {self.weights_path} ...")
        try:
            self._model = YOLO(self.weights_path)

            # Move to correct device
            if self._device != "cpu":
                self._model.to(self._device)

            # Set default inference parameters
            log_info(
                f"[ModelLoader] Model loaded ✓ — "
                f"device={self._device}, "
                f"conf={self.confidence}, "
                f"iou={self.iou}"
            )

        except Exception as e:
            log_error(f"[ModelLoader] Failed to load model: {e}")
            raise RuntimeError(f"[ModelLoader] Model load failed: {e}")

