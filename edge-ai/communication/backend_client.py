"""
Backend REST Client — HTTP communication with BIZmate Flask API
Handles device registration, heartbeat, camera events, sensor readings, footfall.

All methods return True on success, False on failure.
Includes exponential-backoff retry and offline event buffering.
"""

import json
import time
import threading
from typing import Optional, List, Dict, Any

import requests
from requests.exceptions import RequestException, Timeout, ConnectionError


from ..utils.logger import log_info, log_warning, log_error, log_debug
from ..config import EdgeAIConfig
from ..events.event_types import CameraEvent, SensorEvent, FootfallEvent, HeartbeatEvent


# ─────────────────────────────────────────────────────────────────────────────
# Offline buffer — events queued while backend is unreachable
# ─────────────────────────────────────────────────────────────────────────────
_OFFLINE_BUFFER_MAX = 200


class BackendClient:
    """
    HTTP client for all BIZmate backend API calls.

    Args:
        base_url:       Flask backend root URL (e.g. 'http://127.0.0.1:5000')
        device_id:      Backend-registered device ID
        api_key:        Optional API key sent as X-API-Key header
        timeout:        Request timeout in seconds
        retry_attempts: Number of retries on network failure
        backoff:        Seconds to wait between retries (doubles each attempt)
    """

    def __init__(
        self,
        base_url: str = EdgeAIConfig.BACKEND_API_URL,
        device_id: str = EdgeAIConfig.DEVICE_ID,
        api_key: str = EdgeAIConfig.BACKEND_API_KEY,
        timeout: int = EdgeAIConfig.REQUEST_TIMEOUT_SECONDS,
        retry_attempts: int = EdgeAIConfig.RECONNECT_RETRY_ATTEMPTS,
        backoff: int = EdgeAIConfig.RECONNECT_BACKOFF_SECONDS,
    ):
        self.base_url = base_url.rstrip("/")
        self.device_id = device_id
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.backoff = backoff

        # Build session with default headers
        self._session = requests.Session()
        self._session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Device-ID": device_id,
        })
        if api_key:
            self._session.headers["X-API-Key"] = api_key

        # Offline buffer — stored when backend is unreachable
        self._offline_buffer: List[Dict] = []
        self._offline_lock = threading.Lock()

        # Connectivity tracking
        self._backend_reachable = False
        self._last_success_time: Optional[float] = None

        log_info(f"[BackendClient] Initialized → {self.base_url}")

    # ─────────────────────────────────────────────────────────────────────────
    # DEVICE MANAGEMENT
    # ─────────────────────────────────────────────────────────────────────────

    def register_device(self) -> bool:
        """
        Register this edge device with the backend.
        Maps to: POST /devices/register

        Returns:
            True if registration succeeded or device already exists.
        """
        payload = {
            "device_id": self.device_id,
            "name": EdgeAIConfig.DEVICE_NAME,
            "device_type": EdgeAIConfig.DEVICE_TYPE,
            "location": EdgeAIConfig.DEVICE_LOCATION,
            "ip_address": EdgeAIConfig.IP_ADDRESS or self._get_local_ip(),
            "mac_address": EdgeAIConfig.MAC_ADDRESS,
            "firmware_version": EdgeAIConfig.FIRMWARE_VERSION,
            "status": "online",
        }
        success, _ = self._post("/devices/register", payload)
        if success:
            log_info(f"[BackendClient] Device registered: {self.device_id}")
        else:
            log_warning(
                f"[BackendClient] Device registration failed — will retry on heartbeat"
            )
        return success

    def send_heartbeat(self, event: HeartbeatEvent) -> bool:
        """
        Send device keepalive ping.
        Maps to: POST /devices/heartbeat

        Args:
            event: HeartbeatEvent with current device status.

        Returns:
            True if backend acknowledged.
        """
        success, _ = self._post("/devices/heartbeat", event.to_backend_payload())
        if success:
            self._last_success_time = time.time()
            log_debug("[BackendClient] Heartbeat sent")
        else:
            log_warning("[BackendClient] Heartbeat failed")
        return success

    # ─────────────────────────────────────────────────────────────────────────
    # CAMERA EVENTS
    # ─────────────────────────────────────────────────────────────────────────

    def post_camera_event(self, event: CameraEvent) -> bool:
        """
        Post a vision detection event.
        Maps to: POST /monitoring/camera-events

        Args:
            event: CameraEvent to post.

        Returns:
            True if accepted by backend.
        """
        success, resp = self._post(
            "/monitoring/camera-events", event.to_backend_payload()
        )
        if success:
            log_debug(f"[BackendClient] Camera event posted: {event.event_type}")
        else:
            log_warning(f"[BackendClient] Camera event failed: {event.event_type}")
            self._buffer_offline(
                "/monitoring/camera-events", event.to_backend_payload()
            )
        return success

    # ─────────────────────────────────────────────────────────────────────────
    # FOOTFALL
    # ─────────────────────────────────────────────────────────────────────────

    def post_footfall(self, event: FootfallEvent) -> bool:
        """
        Post a visitor count event.
        Maps to: POST /monitoring/footfall

        Args:
            event: FootfallEvent to post.

        Returns:
            True if accepted.
        """
        success, _ = self._post("/monitoring/footfall", event.to_backend_payload())
        if success:
            log_debug(
                f"[BackendClient] Footfall posted: "
                f"entry={event.entry_count}, exit={event.exit_count}, "
                f"occupancy={event.current_occupancy}"
            )
        else:
            self._buffer_offline("/monitoring/footfall", event.to_backend_payload())
        return success

    # ─────────────────────────────────────────────────────────────────────────
    # SENSOR READINGS
    # ─────────────────────────────────────────────────────────────────────────

    def post_sensor_reading(self, event: SensorEvent) -> bool:
        """
        Post a sensor telemetry reading.
        Maps to: POST /sensors/readings

        Args:
            event: SensorEvent to post.

        Returns:
            True if accepted.
        """
        success, _ = self._post("/sensors/readings", event.to_backend_payload())
        if success:
            log_debug(
                f"[BackendClient] Sensor reading posted: "
                f"{event.sensor_type}={event.value}{event.unit}"
                + (" [ANOMALY]" if event.is_anomaly else "")
            )
        else:
            self._buffer_offline("/sensors/readings", event.to_backend_payload())
        return success

    # ─────────────────────────────────────────────────────────────────────────
    # OFFLINE BUFFER FLUSH
    # ─────────────────────────────────────────────────────────────────────────

    def flush_offline_buffer(self) -> int:
        """
        Attempt to send all buffered offline events.
        Called automatically when backend becomes reachable again.

        Returns:
            Number of events successfully flushed.
        """
        with self._offline_lock:
            if not self._offline_buffer:
                return 0
            buffer_snapshot = list(self._offline_buffer)
            self._offline_buffer.clear()

        flushed = 0
        re_buffer = []

        for item in buffer_snapshot:
            endpoint = item["endpoint"]
            payload = item["payload"]
            success, _ = self._post(endpoint, payload, _is_retry=True)
            if success:
                flushed += 1
            else:
                re_buffer.append(item)

        # Put back failed ones
        if re_buffer:
            with self._offline_lock:
                self._offline_buffer = re_buffer + self._offline_buffer
                self._offline_buffer = self._offline_buffer[:_OFFLINE_BUFFER_MAX]

        if flushed > 0:
            log_info(f"[BackendClient] Flushed {flushed} offline-buffered events")

        return flushed

    def offline_buffer_size(self) -> int:
        """Return number of events currently in offline buffer."""
        return len(self._offline_buffer)

    # ─────────────────────────────────────────────────────────────────────────
    # HEALTH CHECK
    # ─────────────────────────────────────────────────────────────────────────

    def is_backend_reachable(self) -> bool:
        """
        Quick health check — GET /auth/login or root endpoint.

        Returns:
            True if backend responds with any HTTP status.
        """
        try:
            resp = self._session.get(
                f"{self.base_url}/",
                timeout=3,
            )
            return resp.status_code < 500
        except Exception:
            return False

    # ─────────────────────────────────────────────────────────────────────────
    # INTERNAL HTTP
    # ─────────────────────────────────────────────────────────────────────────

    def _post(
        self,
        endpoint: str,
        payload: Dict[str, Any],
        _is_retry: bool = False,
    ):
        """
        Internal POST with retry + exponential backoff.

        Args:
            endpoint:   URL path (e.g. '/monitoring/camera-events')
            payload:    Dictionary to JSON-encode and POST
            _is_retry:  True if this is a retry (skip offline buffering)

        Returns:
            tuple: (success: bool, response_json: dict or None)
        """
        url = f"{self.base_url}{endpoint}"
        last_error = None

        for attempt in range(1, self.retry_attempts + 1):
            try:
                resp = self._session.post(
                    url,
                    json=payload,
                    timeout=self.timeout,
                )

                if resp.status_code in (200, 201):
                    self._backend_reachable = True
                    self._last_success_time = time.time()
                    # Flush offline buffer on successful connection
                    if self.offline_buffer_size() > 0 and not _is_retry:
                        threading.Thread(
                            target=self.flush_offline_buffer, daemon=True
                        ).start()
                    try:
                        return True, resp.json()
                    except Exception:
                        return True, {}

                elif resp.status_code == 409:
                    # Conflict (device already registered) — treat as success
                    log_debug(f"[BackendClient] {endpoint} → 409 Conflict (OK)")
                    return True, {}

                else:
                    log_warning(
                        f"[BackendClient] {endpoint} → HTTP {resp.status_code} "
                        f"(attempt {attempt}/{self.retry_attempts})"
                    )
                    last_error = f"HTTP {resp.status_code}"

            except (ConnectionError, Timeout) as e:
                self._backend_reachable = False
                last_error = str(e)
                log_warning(
                    f"[BackendClient] {endpoint} → Connection error "
                    f"(attempt {attempt}/{self.retry_attempts}): {e}"
                )

            except RequestException as e:
                last_error = str(e)
                log_error(f"[BackendClient] {endpoint} → Request exception: {e}")

            except Exception as e:
                last_error = str(e)
                log_error(f"[BackendClient] {endpoint} → Unexpected error: {e}")

            # Backoff before retry (skip on last attempt)
            if attempt < self.retry_attempts:
                wait_time = self.backoff * (2 ** (attempt - 1))  # exponential
                log_debug(f"[BackendClient] Retrying in {wait_time}s...")
                time.sleep(wait_time)

        log_error(f"[BackendClient] {endpoint} → All {self.retry_attempts} attempts failed: {last_error}")
        return False, None

    def _buffer_offline(self, endpoint: str, payload: Dict[str, Any]):
        """Add a failed request to offline buffer for later retry."""
        with self._offline_lock:
            if len(self._offline_buffer) < _OFFLINE_BUFFER_MAX:
                self._offline_buffer.append({
                    "endpoint": endpoint,
                    "payload": payload,
                    "buffered_at": time.time(),
                })
                log_debug(
                    f"[BackendClient] Buffered offline: {endpoint} "
                    f"(total buffered: {len(self._offline_buffer)})"
                )
            else:
                log_warning(
                    "[BackendClient] Offline buffer full — dropping oldest event"
                )
                self._offline_buffer.pop(0)
                self._offline_buffer.append({
                    "endpoint": endpoint,
                    "payload": payload,
                    "buffered_at": time.time(),
                })

    @staticmethod
    def _get_local_ip() -> str:
        """Try to detect local IP address."""
        import socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"
