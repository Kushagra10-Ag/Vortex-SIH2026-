from datetime import datetime, timedelta

from app.db import db
from app.models import Device
from flask import current_app


def register_device(data):
    """
    Register a new device.
    """

    existing = Device.query.filter_by(
        device_id=data["device_id"]
    ).first()

    if existing:
        raise ValueError("Device already registered.")

    device = Device(
        device_id=data["device_id"],
        name=data["name"],
        device_type=data["device_type"],
        location=data.get("location", "Store"),
        status="online",
        last_heartbeat=datetime.utcnow()
    )

    db.session.add(device)
    db.session.commit()

    return device.to_dict()


def get_all_devices(status=None, device_type=None):

    update_offline_devices(current_app.config.get("DEVICE_OFFLINE_TIMEOUT_MINUTES", 5))

    query = Device.query.order_by(
        Device.created_at.desc()
    )
    if status:
        query = query.filter_by(status=status)
    if device_type:
        query = query.filter_by(device_type=device_type)
    devices = query.all()

    return [
        device.to_dict()
        for device in devices
    ]


def get_device(device_id):

    device = Device.query.filter_by(
        device_id=device_id
    ).first()

    if not device:
        raise ValueError("Device not found.")

    return device.to_dict()


def update_device(device_id, data):

    device = Device.query.filter_by(
        device_id=device_id
    ).first()

    if not device:
        raise ValueError("Device not found.")

    if "name" in data:
        device.name = data["name"]

    if "device_type" in data:
        device.device_type = data["device_type"]

    if "location" in data:
        device.location = data["location"]

    if "status" in data:
        device.status = data["status"]

    db.session.commit()

    return device.to_dict()


def delete_device(device_id):

    device = Device.query.filter_by(
        device_id=device_id
    ).first()

    if not device:
        raise ValueError("Device not found.")

    db.session.delete(device)
    db.session.commit()

    return {
        "message": "Device deleted successfully."
    }


def heartbeat(device_id):

    """
    Called by Edge AI every few seconds.
    """

    device = Device.query.filter_by(
        device_id=device_id
    ).first()

    if not device:
        raise ValueError("Device not found.")

    device.status = "online"
    device.last_heartbeat = datetime.utcnow()

    db.session.commit()

    return device.to_dict()


def update_offline_devices(timeout_minutes=5):

    """
    Mark devices offline if heartbeat is too old.
    """

    threshold = datetime.utcnow() - timedelta(
        minutes=timeout_minutes
    )

    devices = Device.query.all()

    updated = 0

    for device in devices:

        if (
            device.last_heartbeat and
            device.last_heartbeat < threshold and
            device.status != "offline"
        ):

            device.status = "offline"
            updated += 1

    db.session.commit()

    return {
        "offline_updated": updated
    }


def get_devices_by_status(status):

    devices = Device.query.filter_by(
        status=status
    ).all()

    return [
        device.to_dict()
        for device in devices
    ]


def get_devices_by_type(device_type):

    devices = Device.query.filter_by(
        device_type=device_type
    ).all()

    return [
        device.to_dict()
        for device in devices
    ]


def get_device_summary():

    total = Device.query.count()

    online = Device.query.filter_by(
        status="online"
    ).count()

    offline = Device.query.filter_by(
        status="offline"
    ).count()

    warning = Device.query.filter_by(
        status="warning"
    ).count()

    cameras = Device.query.filter_by(
        device_type="camera"
    ).count()

    ir = Device.query.filter_by(
        device_type="ir_sensor"
    ).count()

    ultrasonic = Device.query.filter_by(
        device_type="ultrasonic_sensor"
    ).count()

    return {
        "total_devices": total,
        "online_devices": online,
        "offline_devices": offline,
        "warning_devices": warning,
        "camera_count": cameras,
        "ir_sensor_count": ir,
        "ultrasonic_sensor_count": ultrasonic
    }


def get_device_by_id(device_id):
    device = Device.query.get(device_id)
    if not device:
        raise ValueError("Device not found.")
    return device.to_dict()


def record_heartbeat(data):
    device_id = data.get("device_id")
    if not device_id:
        raise ValueError("device_id is required.")
    return heartbeat(device_id)