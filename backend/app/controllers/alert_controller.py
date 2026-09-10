from app.services import alert_service

def create_alert(data):
    return alert_service.create_alert(data)


def get_active_alerts(severity=None, limit=50):
    return alert_service.get_active_alerts(severity=severity, limit=limit)


def get_alert_history(limit=100):
    return alert_service.get_alert_history(limit=limit)


def mark_as_read(alert_id):
    return alert_service.mark_as_read(alert_id)


def resolve_alert(alert_id, data=None):
    return alert_service.resolve_alert(alert_id, data=data)


def get_alert_counts():
    return alert_service.get_alert_counts()

