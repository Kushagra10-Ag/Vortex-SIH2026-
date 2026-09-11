"""
Communication Package — Re-exports all communication components
"""

from .backend_client import BackendClient
from .websocket_client import WebSocketClient

__all__ = [
    "BackendClient",
    "WebSocketClient",
]

