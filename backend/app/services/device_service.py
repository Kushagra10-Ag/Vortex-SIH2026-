from datetime import datetime
from app.db import db
from app.models import Device

def register_device(data):
    device_id = data.get("device_id")
    name = data.get("name")
    device_type = data.get("device_type")

    if not device_id or not name or not device_type:
        return {"error": "device_id, name, and device_type are required"}, 400

    existing = Device.query.filter_by(device_id=device_id).first()
    if existing:
        return {"error": f"Device with ID '{device_id}' already registered"}, 400

    device = Device(
        device_id=device_id.strip(),
        name=name.strip(),
        device_type=device_type.strip(),
        location=data.get("location", "Store Floor"),
        ip_address=data.get("ip_address"),
        mac_address=data.get("mac_address"),
        status=data.get("status", "online"),
        firmware_version=data.get("firmware_version", "1.0.0"),
        config_meta=data.get("config_meta", {}),
        last_heartbeat=datetime.utcnow()
    )

    db.session.add(device)
    db.session.commit()

    return {
        "message": "Device registered successfully",
        "device": device.to_dict()
    }, 201


def get_all_devices(status=None, device_type=None):
    query = Device.query
    if status:
        query = query.filter_by(status=status)
    if device_type:
        query = query.filter_by(device_type=device_type)

    devices = query.order_by(Device.created_at.desc()).all()
    return [d.to_dict() for d in devices]


def get_device_by_id(device_id):
    device = Device.query.get(device_id)
    if not device:
        # Try lookup by device_id string
        device = Device.query.filter_by(device_id=str(device_id)).first()

    if not device:
        return {"error": "Device not found"}, 404

    return {"device": device.to_dict()}, 200


def update_device(device_id, data):
    device = Device.query.get(device_id)
    if not device:
        device = Device.query.filter_by(device_id=str(device_id)).first()

    if not device:
        return {"error": "Device not found"}, 404

    if "name" in data:
        device.name = data["name"]
    if "location" in data:
        device.location = data["location"]
    if "status" in data:
        device.status = data["status"]
    if "ip_address" in data:
        device.ip_address = data["ip_address"]
    if "mac_address" in data:
        device.mac_address = data["mac_address"]
    if "firmware_version" in data:
        device.firmware_version = data["firmware_version"]
    if "config_meta" in data:
        device.config_meta = data["config_meta"]

    db.session.commit()
    return {"message": "Device updated successfully", "device": device.to_dict()}, 200


def delete_device(device_id):
    device = Device.query.get(device_id)
    if not device:
        device = Device.query.filter_by(device_id=str(device_id)).first()

    if not device:
        return {"error": "Device not found"}, 404

    db.session.delete(device)
    db.session.commit()
    return {"message": "Device deleted successfully"}, 200


def record_heartbeat(data):
    device_id = data.get("device_id")
    if not device_id:
        return {"error": "device_id is required"}, 400

    device = Device.query.filter_by(device_id=str(device_id)).first()
    now = datetime.utcnow()

    if not device:
        # Auto-register device on initial heartbeat if requested
        if data.get("auto_register"):
            device = Device(
                device_id=device_id,
                name=data.get("name", f"Device {device_id}"),
                device_type=data.get("device_type", "gateway"),
                location=data.get("location", "Store Floor"),
                ip_address=data.get("ip_address"),
                status="online",
                last_heartbeat=now
            )
            db.session.add(device)
            db.session.commit()
            return {"message": "Device registered and heartbeat recorded", "device": device.to_dict()}, 201
        return {"error": "Device not found"}, 404

    device.last_heartbeat = now
    device.status = data.get("status", "online")
    if "ip_address" in data:
        device.ip_address = data["ip_address"]
    if "firmware_version" in data:
        device.firmware_version = data["firmware_version"]

    db.session.commit()
    return {
        "message": "Heartbeat acknowledged",
        "device_id": device.device_id,
        "status": device.status,
        "last_heartbeat": now.isoformat()
    }, 200

