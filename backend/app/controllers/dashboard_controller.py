from app.services import dashboard_service

def get_dashboard_overview():
    return dashboard_service.get_dashboard_overview()


def get_realtime_telemetry():
    return dashboard_service.get_realtime_telemetry()

