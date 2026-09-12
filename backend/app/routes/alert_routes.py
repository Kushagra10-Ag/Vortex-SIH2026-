from flask import Blueprint, request, jsonify
from app.controllers import alert_controller
from app.middleware.auth import device_api_key_required, token_required

alert_bp = Blueprint("alert", __name__)

@alert_bp.route("", methods=["POST"])
@device_api_key_required
def create_alert():
    data = request.get_json() or {}
    res, status_code = alert_controller.create_alert(data)
    return jsonify(res), status_code


@alert_bp.route("", methods=["GET"])
@alert_bp.route("/list", methods=["GET"])
@token_required
def get_alerts():
    severity = request.args.get("severity")
    limit = int(request.args.get("limit", 50))
    resolved = request.args.get("resolved")

    if resolved == "all":
        alerts = alert_controller.get_alert_history(limit=limit)
    else:
        alerts = alert_controller.get_active_alerts(severity=severity, limit=limit)

    return jsonify({"success": True, "alerts": alerts}), 200


@alert_bp.route("/counts", methods=["GET"])
@token_required
def get_alert_counts():
    counts = alert_controller.get_alert_counts()
    return jsonify({"success": True, "counts": counts}), 200


@alert_bp.route("/<int:alert_id>/read", methods=["PUT", "PATCH"])
@token_required
def mark_alert_read(alert_id):
    res, status_code = alert_controller.mark_as_read(alert_id)
    return jsonify(res), status_code


@alert_bp.route("/<int:alert_id>/resolve", methods=["PUT", "PATCH"])
@token_required
def resolve_alert(alert_id):
    data = request.get_json() or {}
    res, status_code = alert_controller.resolve_alert(alert_id, data=data)
    return jsonify(res), status_code

