"""
Camera Package — Stream ingest for USB, IP Webcam, and RTSP
"""

from .reconnect import ReconnectWatchdog
from .stream_handler import StreamHandler
from .frame_processor import FrameProcessor
from .mobile_camera import MobileCamera, resolve_camera_source, build_ip_webcam_url

__all__ = [
    "ReconnectWatchdog",
    "StreamHandler",
    "FrameProcessor",
    "MobileCamera",
    "resolve_camera_source",
    "build_ip_webcam_url",
]
