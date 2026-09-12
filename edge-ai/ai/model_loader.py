"""
Model Loader — Load YOLOv11 Weights via Ultralytics API
Loads the YOLO model from the weights/ directory and prepares it for inference.

Supports:
  - Local file at EdgeAIConfig.YOLO_WEIGHTS_PATH (default weights/yolov11.pt)
  - First-run download of EdgeAIConfig.YOLO_MODEL_NAME (default yolo11n.pt)
  - CPU or CUDA GPU inference via config.ENABLE_GPU
  - Graceful failure with clear error messages

Usage:
    loader = ModelLoader()
    model = loader.load()
"""

import os
import shutil
from typing import Optional

from utils.logger import log_info, log_warning, log_error
from config import EdgeAIConfig


_EDGE_AI_ROOT = os.path.dirname(os.path.dirname(__file__))

# Default cache path relative to edge-ai root (plan.md: weights/yolov11.pt)
_DEFAULT_WEIGHTS = os.path.join(_EDGE_AI_ROOT, "weights", "yolov11.pt")

# COCO names file
_DEFAULT_NAMES = os.path.join(_EDGE_AI_ROOT, "weights", "coco.names")


def _resolve_weights_path(weights_path: Optional[str] = None) -> str:
    """Resolve YOLO_WEIGHTS_PATH against the edge-ai directory when relative."""
    raw = weights_path if weights_path is not None else EdgeAIConfig.YOLO_WEIGHTS_PATH
    if not raw:
        return _DEFAULT_WEIGHTS
    if os.path.isabs(raw):
        return raw
    return os.path.normpath(os.path.join(_EDGE_AI_ROOT, raw))


def _normalize_model_name(name: str) -> str:
    """Ensure an Ultralytics checkpoint name ends with .pt."""
    text = (name or "").strip()
    if not text:
        return "yolo11n.pt"
    if text.lower().endswith(".pt"):
        return text
    return f"{text}.pt"


def _is_usable_weights_file(path: str) -> bool:
    """True when path is a non-empty file (0-byte placeholders are not usable)."""
    return os.path.isfile(path) and os.path.getsize(path) > 0


class ModelLoader:
    """
    Loads and configures a YOLO model for edge inference.

    Args:
        weights_path:  Path to .pt weights file. Defaults to YOLO_WEIGHTS_PATH.
        model_name:    Ultralytics pretrained name if local weights are missing.
        use_gpu:       Use CUDA GPU if True (requires CUDA build of PyTorch).
        confidence:    Default confidence threshold for predictions.
        iou:           Default IoU threshold for NMS.
    """

    def __init__(
        self,
        weights_path: Optional[str] = None,
        model_name: Optional[str] = None,
        use_gpu: bool = EdgeAIConfig.ENABLE_GPU,
        confidence: float = EdgeAIConfig.MODEL_CONFIDENCE_THRESHOLD,
        iou: float = EdgeAIConfig.MODEL_IOU_THRESHOLD,
    ):
        self.weights_path = _resolve_weights_path(weights_path)
        self.model_name = _normalize_model_name(
            model_name if model_name is not None else EdgeAIConfig.YOLO_MODEL_NAME
        )
        self.use_gpu = use_gpu
        self.confidence = confidence
        self.iou = iou

        self._model = None
        self._class_names: list = []
        self._device: str = "cpu"
        self._loaded_from: str = ""

    # ─────────────────────────────────────────────────────────────────────────
    # PUBLIC API
    # ─────────────────────────────────────────────────────────────────────────

    def load(self):
        """
        Load YOLO model from local weights, or download YOLO_MODEL_NAME on first run.

        Returns:
            ultralytics.YOLO: Loaded model ready for .predict() calls.

        Raises:
            RuntimeError: If ultralytics is missing or the model cannot be loaded.
        """
        if self._model is not None:
            log_warning("[ModelLoader] Model already loaded — returning cached instance")
            return self._model

        source = self._resolve_load_source()
        self._determine_device()
        self._load_class_names()
        self._load_model(source)
        self._cache_weights_locally(source)

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

    def _resolve_load_source(self) -> str:
        """Prefer a real local .pt; otherwise use the pretrained Ultralytics name."""
        if _is_usable_weights_file(self.weights_path):
            size_mb = os.path.getsize(self.weights_path) / (1024 * 1024)
            log_info(
                f"[ModelLoader] Found weights: {self.weights_path} ({size_mb:.1f} MB)"
            )
            return self.weights_path

        if os.path.isfile(self.weights_path) and os.path.getsize(self.weights_path) == 0:
            log_warning(
                f"[ModelLoader] {self.weights_path} is empty — "
                f"downloading {self.model_name} on first run"
            )
        else:
            log_warning(
                f"[ModelLoader] Weights not found at {self.weights_path} — "
                f"downloading {self.model_name} on first run"
            )
        return self.model_name

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
        if os.path.isfile(_DEFAULT_NAMES) and os.path.getsize(_DEFAULT_NAMES) > 0:
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

    def _load_model(self, source: str):
        """Import ultralytics and load YOLO from a local path or pretrained name."""
        try:
            from ultralytics import YOLO
        except ImportError:
            raise RuntimeError(
                "[ModelLoader] 'ultralytics' package not installed.\n"
                "Install with: pip install ultralytics"
            )

        log_info(f"[ModelLoader] Loading YOLO model from {source} ...")
        try:
            self._model = YOLO(source)
            self._loaded_from = source

            if self._device != "cpu":
                self._model.to(self._device)

            log_info(
                f"[ModelLoader] Model loaded ✓ — "
                f"source={source}, "
                f"device={self._device}, "
                f"conf={self.confidence}, "
                f"iou={self.iou}"
            )

        except Exception as e:
            log_error(f"[ModelLoader] Failed to load model: {e}")
            raise RuntimeError(f"[ModelLoader] Model load failed: {e}")

    def _cache_weights_locally(self, source: str):
        """Copy a downloaded checkpoint into weights/yolov11.pt for the next start."""
        if _is_usable_weights_file(self.weights_path):
            return
        if self._model is None:
            return

        candidates = []
        ckpt = getattr(self._model, "ckpt_path", None)
        if ckpt:
            candidates.append(str(ckpt))
        if source and os.path.isfile(source):
            candidates.append(source)
        candidates.append(os.path.join(os.getcwd(), os.path.basename(self.model_name)))

        src = next((p for p in candidates if _is_usable_weights_file(p)), None)
        if src is None:
            log_warning(
                "[ModelLoader] Download succeeded but could not find a file to cache "
                f"at {self.weights_path}"
            )
            return

        try:
            os.makedirs(os.path.dirname(self.weights_path), exist_ok=True)
            if os.path.abspath(src) != os.path.abspath(self.weights_path):
                shutil.copy2(src, self.weights_path)
            log_info(f"[ModelLoader] Cached weights to {self.weights_path}")
        except Exception as e:
            log_warning(f"[ModelLoader] Could not cache weights locally: {e}")
