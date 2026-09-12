from flask import Blueprint, request, jsonify
from app.controllers import sensor_controller
from app.middleware.auth import device_api_key_required, token_required

sensor_bp = Blueprint("sensor", __name__)

@sensor_bp.route("/readings", methods=["POST"])
@device_api_key_required
def record_reading():
    data = request.get_json() or {}
    res, status_code = sensor_controller.record_reading(data)
    return jsonify(res), status_code


@sensor_bp.route("/readings/latest", methods=["GET"])
@token_required
def get_latest_readings():
    sensor_type = request.args.get("type")
    limit = int(request.args.get("limit", 50))
    readings = sensor_controller.get_latest_readings(sensor_type=sensor_type, limit=limit)
    return jsonify({"success": True, "readings": readings}), 200


@sensor_bp.route("/readings/history/<string:sensor_id>", methods=["GET"])
@token_required
def get_sensor_history(sensor_id):
    hours = int(request.args.get("hours", 24))
    history = sensor_controller.get_sensor_history(sensor_id, hours=hours)
    return jsonify({"success": True, "sensor_id": sensor_id, "history": history}), 200


@sensor_bp.route("/summary", methods=["GET"])
@token_required
def get_sensor_summary():
    summary = sensor_controller.get_sensor_summary()
    return jsonify({"success": True, "summary": summary}), 200

