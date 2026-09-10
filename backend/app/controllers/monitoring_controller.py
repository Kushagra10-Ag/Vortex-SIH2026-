from app.services import monitoring_service

def get_realtime_status():
    return monitoring_service.get_realtime_status()


def log_camera_event(data):
    return monitoring_service.record_camera_event(data)


def get_camera_events(limit=50, event_type=None):
    return monitoring_service.get_camera_events(limit=limit, event_type=event_type)


def get_shelf_statuses():
    return monitoring_service.get_shelf_statuses()


def update_shelf(shelf_id, data):
    return monitoring_service.update_shelf_status(shelf_id, data)


def log_footfall(data):
    return monitoring_service.record_footfall(data)


def get_footfall_stats(timeframe="today"):
    return monitoring_service.get_footfall_analytics(timeframe=timeframe)

