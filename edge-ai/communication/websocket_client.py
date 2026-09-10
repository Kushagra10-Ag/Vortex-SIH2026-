"""
WebSocket Client — Optional Real-Time Event Channel
Provides async bidirectional communication with BIZmate backend.

Falls back gracefully to REST-only mode if:
  - websockets package not installed
  - Backend has no WS endpoint
  - Connection fails

Usage:
    ws = WebSocketClient(url="ws://127.0.0.1:5000/ws")
    asyncio.run(ws.connect())
"""

import asyncio
import json
import threading
import time
from typing import Optional, Callable, Any

from ..utils.logger import log_info, log_warning, log_error, log_debug
from ..config import EdgeAIConfig

# Graceful import — websockets is optional
try:
    import websockets
    from websockets.exceptions import WebSocketException, ConnectionClosed
    _WS_AVAILABLE = True
except ImportError:
    _WS_AVAILABLE = False
    log_warning(
        "[WebSocketClient] 'websockets' package not installed — "
        "running in REST-only mode"
    )


class WebSocketClient:
    """
    Async WebSocket client for real-time backend communication.

    When connected, the edge device can:
      - Receive configuration updates from backend
      - Push events with lower latency than HTTP batching
      - Receive remote commands (e.g., capture snapshot on demand)

    REST mode is the primary channel; WebSocket is supplementary.

    Args:
        ws_url:         WebSocket URL (e.g. 'ws://127.0.0.1:5000/ws/edge')
        device_id:      Device ID sent on connect handshake
        on_message:     Callback called with received message dict
        reconnect_delay: Seconds between reconnect attempts
    """

    def __init__(
        self,
        ws_url: Optional[str] = None,
        device_id: str = EdgeAIConfig.DEVICE_ID,
        on_message: Optional[Callable[[dict], None]] = None,
        reconnect_delay: int = 10,
    ):
        # Build WS URL from backend URL if not provided
        if ws_url is None:
            http_url = EdgeAIConfig.BACKEND_API_URL
            ws_url = http_url.replace("http://", "ws://").replace("https://", "wss://")
            ws_url = ws_url.rstrip("/") + "/ws/edge"

        self.ws_url = ws_url
        self.device_id = device_id
        self.on_message = on_message
        self.reconnect_delay = reconnect_delay

        self._connection = None
        self._is_connected = False
        self._is_running = False
        self._event_loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None

    # ─────────────────────────────────────────────────────────────────────────
    # PUBLIC API
    # ─────────────────────────────────────────────────────────────────────────

    def start(self):
        """
        Start WebSocket client in a background thread.
        Non-blocking — returns immediately.
        """
        if not _WS_AVAILABLE:
            log_warning(
                "[WebSocketClient] Not starting — websockets not available (REST-only mode)"
            )
            return

        if self._is_running:
            return

        self._is_running = True
        self._thread = threading.Thread(
            target=self._run_loop,
            name="ws-client",
            daemon=True,
        )
        self._thread.start()
        log_info(f"[WebSocketClient] Started → {self.ws_url}")

    def stop(self):
        """Stop WebSocket client and close connection."""
        self._is_running = False
        if self._event_loop and not self._event_loop.is_closed():
            # Schedule close on event loop
            future = asyncio.run_coroutine_threadsafe(
                self._close(), self._event_loop
            )
            try:
                future.result(timeout=5)
            except Exception:
                pass
        log_info("[WebSocketClient] Stopped")

    def send(self, data: dict) -> bool:
        """
        Send a message via WebSocket (fire-and-forget).

        Args:
            data: Dictionary to send as JSON.

        Returns:
            True if scheduled for send, False if not connected.
        """
        if not self._is_connected or self._connection is None:
            return False
        if not _WS_AVAILABLE:
            return False

        try:
            message = json.dumps(data)
            asyncio.run_coroutine_threadsafe(
                self._connection.send(message), self._event_loop
            )
            return True
        except Exception as e:
            log_warning(f"[WebSocketClient] Send failed: {e}")
            return False

    @property
    def is_connected(self) -> bool:
        """True if WebSocket is currently connected."""
        return self._is_connected

    # ─────────────────────────────────────────────────────────────────────────
    # INTERNAL — ASYNC LOOP
    # ─────────────────────────────────────────────────────────────────────────

    def _run_loop(self):
        """Run async event loop in background thread."""
        self._event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._event_loop)
        try:
            self._event_loop.run_until_complete(self._connect_loop())
        finally:
            self._event_loop.close()

    async def _connect_loop(self):
        """Reconnecting WebSocket loop."""
        while self._is_running:
            try:
                await self._connect_and_listen()
            except Exception as e:
                log_warning(
                    f"[WebSocketClient] Connection error: {e} — "
                    f"retrying in {self.reconnect_delay}s"
                )
                self._is_connected = False

            if self._is_running:
                await asyncio.sleep(self.reconnect_delay)

    async def _connect_and_listen(self):
        """Connect and listen for incoming messages."""
        log_info(f"[WebSocketClient] Connecting to {self.ws_url} ...")

        async with websockets.connect(
            self.ws_url,
            ping_interval=20,
            ping_timeout=10,
            close_timeout=5,
        ) as ws:
            self._connection = ws
            self._is_connected = True
            log_info("[WebSocketClient] Connected ✓")

            # Send handshake
            await ws.send(json.dumps({
                "type": "handshake",
                "device_id": self.device_id,
            }))

            # Listen for messages
            async for raw_msg in ws:
                if not self._is_running:
                    break
                try:
                    msg = json.loads(raw_msg)
                    log_debug(f"[WebSocketClient] Received: {msg.get('type', '?')}")
                    if self.on_message:
                        self.on_message(msg)
                except json.JSONDecodeError:
                    log_warning(f"[WebSocketClient] Invalid JSON received: {raw_msg[:100]}")

        self._is_connected = False
        self._connection = None
        log_info("[WebSocketClient] Disconnected")

    async def _close(self):
        """Close the WebSocket connection gracefully."""
        if self._connection and self._is_connected:
            try:
                await self._connection.close()
            except Exception:
                pass
        self._is_connected = False

