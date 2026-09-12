"""
Mobile / IP Camera Source
Resolves EdgeAIConfig.CAMERA_SOURCE into an OpenCV VideoCapture source:

  - '0', '1', ...     → USB webcam index (int)
  - rtsp://...        → RTSP IP camera
  - http(s)://...     → Android IP Webcam MJPEG (or any HTTP stream)
  - existing file     → video file for offline tests

IP Webcam (Android): default stream path is /video on port 8080.
build_ip_webcam_url() only builds a URL; it does not guess if CAMERA_SOURCE
is already a full URL.
"""

import os
from typing import Optional, Union

from .frame_processor import FrameProcessor
from .stream_handler import StreamHandler
from config import EdgeAIConfig
from utils.logger import log_info, log_warning


# Android IP Webcam default MJPEG path (app setting: http://<ip>:8080/video)
_IP_WEBCAM_DEFAULT_PORT = 8080
_IP_WEBCAM_DEFAULT_PATH = "/video"


def resolve_camera_source(source: Optional[str] = None) -> Union[int, str]:
    """
    Parse CAMERA_SOURCE the same way config.py documents it.

    Args:
        source: Raw source string. Defaults to EdgeAIConfig.CAMERA_SOURCE.

    Returns:
        int webcam index or str URL/path for cv2.VideoCapture.
    """
    raw = EdgeAIConfig.CAMERA_SOURCE if source is None else source
    if raw is None:
        return 0

    text = str(raw).strip().strip('"').strip("'")
    if not text:
        return 0

    if text.isdigit() or (text.startswith("-") and text[1:].isdigit()):
        return int(text)

    lowered = text.lower()
    if lowered.startswith(("rtsp://", "rtsps://", "http://", "https://")):
        return text

    if os.path.isfile(text):
        return text

    log_warning(
        f"[MobileCamera] Source is not an index, URL, or file — "
        f"passing through to OpenCV: {text}"
    )
    return text


def build_ip_webcam_url(
    host: str,
    port: int = _IP_WEBCAM_DEFAULT_PORT,
    path: str = _IP_WEBCAM_DEFAULT_PATH,
) -> str:
    """
    Build an Android IP Webcam MJPEG URL.

    Args:
        host: IP or hostname, without scheme (e.g. '192.168.1.20').
        port: App port (default 8080).
        path: Stream path (default '/video').
    """
    host = host.strip()
    if "://" in host:
        raise ValueError(
            "build_ip_webcam_url() expects a host, not a full URL. "
            "Put the full URL in CAMERA_SOURCE instead."
        )
    if ":" in host:
        raise ValueError(
            "Pass port as the port argument, not inside host "
            "(e.g. host='192.168.1.20', port=8080)."
        )
    if not path.startswith("/"):
        path = "/" + path
    return f"http://{host}:{int(port)}{path}"


class MobileCamera:
    """
    High-level camera used by the edge daemon.

    Owns StreamHandler (capture + reconnect) and FrameProcessor (resize).

    Args:
        source: Override CAMERA_SOURCE (index, URL, or file path).
        process_frames: If True, read() resizes to CAMERA_WIDTH x CAMERA_HEIGHT.
    """

    def __init__(
        self,
        source: Optional[Union[int, str]] = None,
        process_frames: bool = True,
    ):
        if source is None:
            resolved = resolve_camera_source(EdgeAIConfig.CAMERA_SOURCE)
        elif isinstance(source, int):
            resolved = source
        else:
            resolved = resolve_camera_source(str(source))

        self.source = resolved
        self.process_frames = process_frames
        self.processor = FrameProcessor(
            width=EdgeAIConfig.CAMERA_WIDTH,
            height=EdgeAIConfig.CAMERA_HEIGHT,
        )
        self.stream = StreamHandler(source=self.source)

        log_info(f"[MobileCamera] Source resolved: {self.source!r}")

    def start(self) -> bool:
        """Open the stream. Returns False if the source cannot be opened."""
        return self.stream.start()

    def stop(self):
        """Release the camera."""
        self.stream.stop()

    def read(self):
        """
        Latest BGR frame (resized when process_frames=True), or None.
        """
        frame = self.stream.read()
        if frame is None:
            return None
        if self.process_frames:
            return self.processor.process(frame)
        return frame

    def is_alive(self) -> bool:
        """True while the reader thread is up and frames are not stale."""
        return self.stream.is_alive()
