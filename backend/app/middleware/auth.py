from functools import wraps
import hmac
import threading
import time
from flask import request, jsonify, current_app
from app.models import User
import jwt

_device_rate_lock = threading.Lock()
_device_rate_windows = {}

def token_required(f):
    """
    Middleware decorator ensuring a valid JWT token is passed in the Authorization header.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"success": False, "error": "Authorization token is missing"}), 401

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return jsonify({"success": False, "error": "Invalid token header format. Use: Bearer <token>"}), 401

        token = parts[1]
        secret_key = current_app.config.get("JWT_SECRET_KEY") or current_app.config.get("SECRET_KEY")
        if not secret_key:
            return jsonify({"success": False, "error": "JWT secret is not configured"}), 503

        try:
            payload = jwt.decode(token, secret_key, algorithms=["HS256"])
            user_id = payload.get("sub") or payload.get("user_id")
            user = User.query.get(user_id) if user_id else None
            if not user:
                return jsonify({"success": False, "error": "User associated with token not found"}), 401
            request.current_user = user
        except jwt.ExpiredSignatureError:
            return jsonify({"success": False, "error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"success": False, "error": "Invalid token"}), 401
        except Exception as e:
            return jsonify({"success": False, "error": f"Authentication error: {str(e)}"}), 401

        return f(*args, **kwargs)
    return decorated


def get_current_user():
    return getattr(request, "current_user", None)


def device_api_key_required(f):
    """Require the configured API key for edge-device write endpoints."""
    @wraps(f)
    def decorated(*args, **kwargs):
        configured_key = current_app.config.get("DEVICE_API_KEY")
        provided_key = request.headers.get("X-API-Key", "")
        if not configured_key:
            return jsonify({"success": False, "error": "Device API key is not configured"}), 503
        if not provided_key or not hmac.compare_digest(provided_key, configured_key):
            return jsonify({"success": False, "error": "Invalid device API key"}), 401

        now = time.monotonic()
        rate_key = (request.remote_addr or "unknown", request.endpoint)
        with _device_rate_lock:
            window = [timestamp for timestamp in _device_rate_windows.get(rate_key, []) if now - timestamp < 60]
            if len(window) >= current_app.config.get("DEVICE_RATE_LIMIT_PER_MINUTE", 120):
                _device_rate_windows[rate_key] = window
                return jsonify({"success": False, "error": "Device request rate limit exceeded"}), 429
            window.append(now)
            _device_rate_windows[rate_key] = window
        return f(*args, **kwargs)
    return decorated

