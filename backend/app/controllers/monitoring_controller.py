from app.services import monitoring_service
from app.utils.validators import validate_camera_event, validate_footfall

def get_realtime_status():
    return monitoring_service.get_realtime_status()


def log_camera_event(data):
    valid, error = validate_camera_event(data)
    if not valid:
        return {"success": False, "error": error}, 400
    return monitoring_service.record_camera_event(data), 201


def get_camera_events(limit=50, event_type=None):
    return monitoring_service.get_camera_events(limit=limit, event_type=event_type)


def get_shelf_statuses():
    return monitoring_service.get_shelf_statuses()


def update_shelf(shelf_id, data):
    return monitoring_service.update_shelf_status(shelf_id, data), 200


def log_footfall(data):
    valid, error = validate_footfall(data)
    if not valid:
        return {"success": False, "error": error}, 400
    return monitoring_service.record_footfall(data), 201


def get_footfall_stats(timeframe="today"):
    return monitoring_service.get_footfall_analytics(timeframe=timeframe)

