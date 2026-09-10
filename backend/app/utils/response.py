from flask import jsonify

def success_response(data=None, message="Success", status_code=200):
    payload = {
        "success": True,
        "message": message,
    }
    if data is not None:
        payload["data"] = data
    return jsonify(payload), status_code


def error_response(message="An error occurred", status_code=400, details=None):
    payload = {
        "success": False,
        "error": message,
    }
    if details is not None:
        payload["details"] = details
    return jsonify(payload), status_code


def paginated_response(items, total, page=1, per_page=20, message="Success"):
    total_pages = (total + per_page - 1) // per_page if per_page > 0 else 1
    return jsonify({
        "success": True,
        "message": message,
        "data": items,
        "pagination": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        }
    }), 200

