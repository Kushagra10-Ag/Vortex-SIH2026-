from datetime import datetime
from app.db import db
from app.models import Alert

def create_alert(data):
    title = data.get("title")
    message = data.get("message")

    if not title or not message:
        return {"error": "title and message are required"}, 400

    alert = Alert(
        title=title.strip(),
        message=message.strip(),
        severity=data.get("severity", "info"),
        category=data.get("category", "system"),
        source_device_id=data.get("source_device_id"),
        created_at=datetime.utcnow()
    )

    db.session.add(alert)
    db.session.commit()

    return {"message": "Alert created successfully", "alert": alert.to_dict()}, 201


def get_active_alerts(severity=None, limit=50):
    query = Alert.query.filter_by(is_resolved=False)
    if severity:
        query = query.filter_by(severity=severity)

    alerts = query.order_by(Alert.created_at.desc()).limit(limit).all()
    return [a.to_dict() for a in alerts]


def get_alert_history(limit=100):
    alerts = Alert.query.order_by(Alert.created_at.desc()).limit(limit).all()
    return [a.to_dict() for a in alerts]


def mark_as_read(alert_id):
    alert = Alert.query.get(alert_id)
    if not alert:
        return {"error": "Alert not found"}, 404

    alert.is_read = True
    db.session.commit()
    return {"message": "Alert marked as read", "alert": alert.to_dict()}, 200


def resolve_alert(alert_id, data=None):
    alert = Alert.query.get(alert_id)
    if not alert:
        return {"error": "Alert not found"}, 404

    data = data or {}
    alert.is_resolved = True
    alert.is_read = True
    alert.resolved_at = datetime.utcnow()
    alert.resolved_by = data.get("resolved_by", "staff")

    db.session.commit()
    return {"message": "Alert resolved successfully", "alert": alert.to_dict()}, 200


def get_alert_counts():
    total_unresolved = Alert.query.filter_by(is_resolved=False).count()
    critical_count = Alert.query.filter_by(is_resolved=False, severity="critical").count()
    warning_count = Alert.query.filter_by(is_resolved=False, severity="warning").count()
    info_count = Alert.query.filter_by(is_resolved=False, severity="info").count()
    unread_count = Alert.query.filter_by(is_read=False).count()

    return {
        "total_unresolved": total_unresolved,
        "critical": critical_count,
        "warning": warning_count,
        "info": info_count,
        "unread": unread_count,
    }

