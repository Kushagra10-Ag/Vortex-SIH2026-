from functools import wraps
from flask import request, jsonify, current_app
from app.models import User
import jwt

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
        secret_key = current_app.config.get("JWT_SECRET_KEY") or current_app.config.get("SECRET_KEY", "super-secret-key")

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

