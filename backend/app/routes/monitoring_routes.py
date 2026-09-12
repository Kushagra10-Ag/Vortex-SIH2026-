from flask import Blueprint, request, jsonify
from app.controllers import monitoring_controller
from app.middleware.auth import device_api_key_required, token_required

monitoring_bp = Blueprint("monitoring", __name__)

@monitoring_bp.route("/realtime", methods=["GET"])
@token_required
def get_realtime_status():
    status = monitoring_controller.get_realtime_status()
    return jsonify({"success": True, "data": status}), 200


@monitoring_bp.route("/camera-events", methods=["POST"])
@device_api_key_required
def log_camera_event():
    data = request.get_json() or {}
    res, status_code = monitoring_controller.log_camera_event(data)
    return jsonify(res), status_code


@monitoring_bp.route("/camera-events", methods=["GET"])
@token_required
def get_camera_events():
    limit = int(request.args.get("limit", 50))
    event_type = request.args.get("type")
    events = monitoring_controller.get_camera_events(limit=limit, event_type=event_type)
    return jsonify({"success": True, "events": events}), 200


@monitoring_bp.route("/shelves", methods=["GET"])
@token_required
def get_shelf_statuses():
    shelves = monitoring_controller.get_shelf_statuses()
    return jsonify({"success": True, "shelves": shelves}), 200


@monitoring_bp.route("/shelves/<int:shelf_id>", methods=["PUT"])
@token_required
def update_shelf(shelf_id):
    data = request.get_json() or {}
    res, status_code = monitoring_controller.update_shelf(shelf_id, data)
    return jsonify(res), status_code


@monitoring_bp.route("/footfall", methods=["POST"])
@device_api_key_required
def log_footfall():
    data = request.get_json() or {}
    res, status_code = monitoring_controller.log_footfall(data)
    return jsonify(res), status_code


@monitoring_bp.route("/footfall", methods=["GET"])
@token_required
def get_footfall_stats():
    timeframe = request.args.get("timeframe", "today")
    analytics = monitoring_controller.get_footfall_stats(timeframe=timeframe)
    return jsonify({"success": True, "analytics": analytics}), 200

