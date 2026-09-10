from functools import wraps
from flask import request, jsonify
from app.utils.constants import UserRole

def roles_required(*allowed_roles):
    """
    Middleware decorator checking if the authenticated user has one of the allowed roles.
    Must be used in combination with @token_required.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = getattr(request, "current_user", None)
            if not user:
                return jsonify({"success": False, "error": "Authentication required before checking permissions"}), 401

            user_role = getattr(user, "role", "cashier")
            if user_role not in allowed_roles:
                return jsonify({
                    "success": False,
                    "error": f"Permission denied. Required roles: {', '.join(allowed_roles)}. Your role: {user_role}"
                }), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    return roles_required(UserRole.ADMIN, UserRole.OWNER)(f)


def owner_required(f):
    return roles_required(UserRole.OWNER)(f)

