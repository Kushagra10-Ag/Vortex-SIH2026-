from flask import Blueprint, jsonify
from app.controllers import dashboard_controller

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/overview", methods=["GET"])
@dashboard_bp.route("", methods=["GET"])
def get_dashboard_overview():
    data = dashboard_controller.get_dashboard_overview()
    return jsonify({"success": True, "dashboard": data}), 200


@dashboard_bp.route("/telemetry", methods=["GET"])
def get_realtime_telemetry():
    telemetry = dashboard_controller.get_realtime_telemetry()
    return jsonify({"success": True, "telemetry": telemetry}), 200

