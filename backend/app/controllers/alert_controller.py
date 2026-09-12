from app.services import alert_service
from app.utils.validators import validate_alert

def create_alert(data):
    valid, error = validate_alert(data)
    if not valid:
        return {"success": False, "error": error}, 400
    return alert_service.create_alert(data), 201


def get_active_alerts(severity=None, limit=50):
    return alert_service.get_active_alerts(severity=severity, limit=limit)


def get_alert_history(limit=100):
    return alert_service.get_alert_history(limit=limit)


def mark_as_read(alert_id):
    return alert_service.mark_as_read(alert_id), 200


def resolve_alert(alert_id, data=None):
    return alert_service.resolve_alert(alert_id, data=data), 200


def get_alert_counts():
    return alert_service.get_alert_counts()

