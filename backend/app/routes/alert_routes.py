from flask import Blueprint, request, jsonify
from app.controllers import alert_controller

alert_bp = Blueprint("alert", __name__)

@alert_bp.route("", methods=["POST"])
def create_alert():
    data = request.get_json() or {}
    res, status_code = alert_controller.create_alert(data)
    return jsonify(res), status_code


@alert_bp.route("", methods=["GET"])
@alert_bp.route("/list", methods=["GET"])
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
def get_alert_counts():
    counts = alert_controller.get_alert_counts()
    return jsonify({"success": True, "counts": counts}), 200


@alert_bp.route("/<int:alert_id>/read", methods=["PUT", "PATCH"])
def mark_alert_read(alert_id):
    res, status_code = alert_controller.mark_as_read(alert_id)
    return jsonify(res), status_code


@alert_bp.route("/<int:alert_id>/resolve", methods=["PUT", "PATCH"])
def resolve_alert(alert_id):
    data = request.get_json() or {}
    res, status_code = alert_controller.resolve_alert(alert_id, data=data)
    return jsonify(res), status_code

