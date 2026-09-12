"""
Stream Handler — OpenCV frame reader with a latest-frame buffer
Opens USB / RTSP / HTTP / file sources, discards warmup frames, and keeps only
the newest frame so RTSP queues do not lag behind real time.

A background thread calls VideoCapture.read(). The main loop should call
read() which returns a copy of the latest BGR frame (or None).

Reconnects via ReconnectWatchdog when reads fail or the stream goes stale.
"""

import os
import threading
import time
from typing import Optional, Union

try:
    import cv2
except ImportError:
    cv2 = None
import numpy as np

from .reconnect import ReconnectWatchdog
from config import EdgeAIConfig
from utils.logger import log_debug, log_error, log_info, log_warning


CameraSource = Union[int, str]


def _open_capture(source: CameraSource) -> Optional[object]:
    """
    Create a cv2.VideoCapture for the given source.

    Uses CAP_DSHOW on Windows webcam indices (avoids long default MSMF hangs).
    Uses CAP_FFMPEG for RTSP/HTTP streams.
    """
    if cv2 is None:
        log_error("[StreamHandler] OpenCV is not installed; install edge-ai requirements")
        return None

    try:
        if isinstance(source, int):
            if os.name == "nt":
                cap = cv2.VideoCapture(source, cv2.CAP_DSHOW)
            else:
                cap = cv2.VideoCapture(source)
        elif isinstance(source, str) and source.lower().startswith(
            ("rtsp://", "rtsps://", "http://", "https://")
        ):
            cap = cv2.VideoCapture(source, cv2.CAP_FFMPEG)
        else:
            cap = cv2.VideoCapture(source)

        if cap is None or not cap.isOpened():
            if cap is not None:
                cap.release()
            return None
        return cap
    except Exception as e:
        log_error(f"[StreamHandler] VideoCapture open failed: {e}")
        return None


def _configure_capture(
    cap: object,
    source: CameraSource,
    width: int,
    height: int,
    fps: int,
):
    """Apply resolution/FPS only for local webcams; keep RTSP native size."""
    try:
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    except Exception:
        pass

    if not isinstance(source, int):
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    cap.set(cv2.CAP_PROP_FPS, fps)


class StreamHandler:
    """
    Threaded OpenCV capture with a single-slot latest-frame buffer.

    Args:
        source:         Webcam index, RTSP/HTTP URL, or video file path.
        width:          Requested width (USB cameras only).
        height:         Requested height (USB cameras only).
        fps:            Requested FPS (USB cameras only).
        warmup_frames:  Frames to discard after each successful open.
        watchdog:       Optional ReconnectWatchdog instance.
    """

    def __init__(
        self,
        source: CameraSource,
        width: int = EdgeAIConfig.CAMERA_WIDTH,
        height: int = EdgeAIConfig.CAMERA_HEIGHT,
        fps: int = EdgeAIConfig.CAMERA_FPS,
        warmup_frames: int = EdgeAIConfig.CAMERA_WARMUP_FRAMES,
        watchdog: Optional[ReconnectWatchdog] = None,
    ):
        self.source = source
        self.width = width
        self.height = height
        self.fps = fps
        self.warmup_frames = max(0, int(warmup_frames))
        self.watchdog = watchdog if watchdog is not None else ReconnectWatchdog()

        self._cap: Optional[cv2.VideoCapture] = None
        self._frame: Optional[np.ndarray] = None
        self._lock = threading.Lock()
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def start(self) -> bool:
        """Open the camera and start the reader thread. Returns False if first open fails."""
        if self._running:
            log_warning("[StreamHandler] Already running")
            return True

        if not self._open(initial=True):
            log_error(f"[StreamHandler] Could not open source: {self.source}")
            return False

        self._running = True
        self._thread = threading.Thread(
            target=self._read_loop,
            name="camera-stream",
            daemon=True,
        )
        self._thread.start()
        log_info(f"[StreamHandler] Started — source={self.source}")
        return True

    def stop(self):
        """Stop the reader thread and release the capture."""
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=5)
            self._thread = None
        self._release_capture()
        with self._lock:
            self._frame = None
        log_info("[StreamHandler] Stopped")

    def release(self):
        """Alias for stop() — matches OpenCV naming."""
        self.stop()

    def read(self) -> Optional[np.ndarray]:
        """
        Return a copy of the latest BGR frame, or None if none yet / stream down.
        """
        with self._lock:
            if self._frame is None:
                return None
            return self._frame.copy()

    def is_opened(self) -> bool:
        """True if a capture object exists and reports opened."""
        return self._cap is not None and self._cap.isOpened()

    def is_alive(self) -> bool:
        """True if capture is open and the watchdog is not stale."""
        return self._running and self.is_opened() and not self.watchdog.is_stale()

    def _open(self, initial: bool = False) -> bool:
        """Open (or reopen) VideoCapture. On reconnect, wait using the watchdog."""
        self._release_capture()

        if not initial:
            # Chunked sleep so stop() can exit without waiting full backoff
            delay = self.watchdog.next_backoff()
            log_debug(f"[StreamHandler] Reconnect backoff {delay:.0f}s")
            deadline = time.time() + delay
            while self._running and time.time() < deadline:
                time.sleep(0.2)
            if not self._running:
                return False
            self.watchdog.mark_reconnect_attempt()

        cap = _open_capture(self.source)
        if cap is None:
            log_warning(f"[StreamHandler] Open failed for source={self.source}")
            return False

        _configure_capture(cap, self.source, self.width, self.height, self.fps)
        self._cap = cap
        self._discard_warmup(initial=initial)
        self.watchdog.reset_after_open()

        actual_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
        actual_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
        log_info(
            f"[StreamHandler] Capture open — "
            f"source={self.source}, size={actual_w}x{actual_h}"
        )
        return True

    def _discard_warmup(self, initial: bool):
        """Drop unstable frames after open. Reconnect uses fewer discards."""
        if self._cap is None:
            return
        n = self.warmup_frames if initial else min(5, self.warmup_frames)
        for _ in range(n):
            ok, _frame = self._cap.read()
            if not ok:
                break
        if n:
            log_debug(f"[StreamHandler] Discarded {n} warmup frames")

    def _read_loop(self):
        while self._running:
            if self._cap is None or not self._cap.isOpened():
                if not self._open(initial=False):
                    continue
                continue

            try:
                ok, frame = self._cap.read()
            except Exception as e:
                log_error(f"[StreamHandler] read() exception: {e}")
                ok, frame = False, None

            if not ok or frame is None or getattr(frame, "size", 0) == 0:
                self.watchdog.record_failure()
                if self.watchdog.should_reconnect():
                    log_warning(
                        "[StreamHandler] Stream unhealthy — reconnecting "
                        f"(failures={self.watchdog.fail_count})"
                    )
                    if not self._open(initial=False):
                        continue
                else:
                    time.sleep(0.01)
                continue

            self.watchdog.record_success()
            with self._lock:
                self._frame = frame

        self._release_capture()

    def _release_capture(self):
        if self._cap is not None:
            try:
                self._cap.release()
            except Exception:
                pass
            self._cap = None
