from flask import Blueprint, jsonify
from app.controllers import dashboard_controller

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard_bp.route("/overview", methods=["GET"])
def overview():
    return jsonify({
        "success": True,
        "data": dashboard_controller.get_dashboard_overview()
    }), 200


@dashboard_bp.route("/realtime", methods=["GET"])
def realtime():
    return jsonify({
        "success": True,
        "data": dashboard_controller.get_realtime_telemetry()
    }), 200


@dashboard_bp.route("/devices", methods=["GET"])
def devices():
    return jsonify({
        "success": True,
        "data": dashboard_controller.get_device_summary()
    }), 200


@dashboard_bp.route("/inventory-summary", methods=["GET"])
def inventory():
    return jsonify({
        "success": True,
        "data": dashboard_controller.get_inventory_summary()
    }), 200


@dashboard_bp.route("/recent-alerts", methods=["GET"])
def alerts():
    return jsonify({
        "success": True,
        "data": dashboard_controller.get_recent_alerts()
    }), 200
@dashboard_bp.route("/full", methods=["GET"])
def full():
    return jsonify({
        "success": True,
        "data": dashboard_controller.get_full_dashboard()
    }), 200
