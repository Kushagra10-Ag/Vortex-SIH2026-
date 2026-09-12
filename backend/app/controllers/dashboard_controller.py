from app.services import dashboard_service


def get_dashboard_overview():
    return dashboard_service.get_dashboard_overview()


def get_realtime_telemetry():
    return dashboard_service.get_realtime_telemetry()


def get_device_summary():
    return dashboard_service.get_device_summary()


def get_inventory_summary():
    return dashboard_service.get_inventory_summary()


def get_recent_alerts():
    return dashboard_service.get_recent_alerts()
def get_full_dashboard():
    return dashboard_service.get_full_dashboard()