from app.services import device_service

def register_device(data):
    return device_service.register_device(data)


def get_devices(status=None, device_type=None):
    return device_service.get_all_devices(status=status, device_type=device_type)


def get_device_detail(device_id):
    return device_service.get_device_by_id(device_id)


def update_device(device_id, data):
    return device_service.update_device(device_id, data)


def delete_device(device_id):
    return device_service.delete_device(device_id)


def record_heartbeat(data):
    return device_service.record_heartbeat(data)

