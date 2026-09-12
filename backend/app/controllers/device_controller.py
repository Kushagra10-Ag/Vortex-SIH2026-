from app.services import device_service
from app.utils.validators import validate_device_registration

def register_device(data):
    valid, error = validate_device_registration(data)
    if not valid:
        return {"success": False, "error": error}, 400
    return device_service.register_device(data), 201


def get_devices(status=None, device_type=None):
    return device_service.get_all_devices(status=status, device_type=device_type)


def get_device_detail(device_id):
    return device_service.get_device_by_id(device_id)


def update_device(device_id, data):
    return device_service.update_device(device_id, data), 200


def delete_device(device_id):
    return device_service.delete_device(device_id), 200


def record_heartbeat(data):
    return device_service.record_heartbeat(data), 200

