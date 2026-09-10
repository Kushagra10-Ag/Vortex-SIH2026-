from flask import Blueprint, request, jsonify
from app.controllers import device_controller

device_bp = Blueprint("device", __name__)

@device_bp.route("/register", methods=["POST"])
def register_device():
    data = request.get_json() or {}
    res, status_code = device_controller.register_device(data)
    return jsonify(res), status_code


@device_bp.route("", methods=["GET"])
@device_bp.route("/list", methods=["GET"])
def get_devices():
    status = request.args.get("status")
    device_type = request.args.get("type")
    devices = device_controller.get_devices(status=status, device_type=device_type)
    return jsonify({"success": True, "devices": devices}), 200


@device_bp.route("/<int:device_id>", methods=["GET"])
def get_device_detail(device_id):
    res, status_code = device_controller.get_device_detail(device_id)
    return jsonify(res), status_code


@device_bp.route("/<int:device_id>", methods=["PUT"])
def update_device(device_id):
    data = request.get_json() or {}
    res, status_code = device_controller.update_device(device_id, data)
    return jsonify(res), status_code


@device_bp.route("/<int:device_id>", methods=["DELETE"])
def delete_device(device_id):
    res, status_code = device_controller.delete_device(device_id)
    return jsonify(res), status_code


@device_bp.route("/heartbeat", methods=["POST"])
def record_heartbeat():
    data = request.get_json() or {}
    res, status_code = device_controller.record_heartbeat(data)
    return jsonify(res), status_code

