from datetime import datetime
from sqlalchemy import desc

from app.db import db
from app.models import Alert, Device


# ==========================================================
# CREATE ALERT
# ==========================================================

def create_alert(data):

    device = None

    if data.get("device_id"):

        device = Device.query.filter_by(
            device_id=data["device_id"]
        ).first()

    alert = Alert(
        title=data["title"],
        message=data["message"],
        severity=data.get("severity", "warning"),
        category=data.get("category"),
        device_id=device.id if device else None,
        is_read=False,
        is_resolved=False,
        created_at=datetime.utcnow()
    )

    db.session.add(alert)
    db.session.commit()

    return alert.to_dict()


# ==========================================================
# GET ALL ALERTS
# ==========================================================

def get_all_alerts():

    alerts = Alert.query.order_by(
        desc(Alert.created_at)
    ).all()

    return [
        alert.to_dict()
        for alert in alerts
    ]


# ==========================================================
# GET UNREAD ALERTS
# ==========================================================

def get_unread_alerts():

    alerts = Alert.query.filter_by(
        is_read=False
    ).order_by(
        desc(Alert.created_at)
    ).all()

    return [
        alert.to_dict()
        for alert in alerts
    ]


# ==========================================================
# GET ACTIVE ALERTS
# ==========================================================

def get_active_alerts(severity=None, limit=50):

    query = Alert.query.filter_by(
        is_resolved=False
    ).order_by(
        desc(Alert.created_at)
    )
    if severity:
        query = query.filter_by(severity=severity)
    alerts = query.limit(limit).all()

    return [
        alert.to_dict()
        for alert in alerts
    ]


# ==========================================================
# GET ALERT
# ==========================================================

def get_alert(alert_id):

    alert = Alert.query.get(alert_id)

    if not alert:
        raise ValueError("Alert not found.")

    return alert.to_dict()


# ==========================================================
# MARK AS READ
# ==========================================================

def mark_as_read(alert_id):

    alert = Alert.query.get(alert_id)

    if not alert:
        raise ValueError("Alert not found.")

    alert.is_read = True

    db.session.commit()

    return alert.to_dict()


# ==========================================================
# RESOLVE ALERT
# ==========================================================

def resolve_alert(alert_id, data=None):

    alert = Alert.query.get(alert_id)

    if not alert:
        raise ValueError("Alert not found.")

    alert.is_resolved = True

    db.session.commit()

    return alert.to_dict()


# ==========================================================
# DELETE ALERT
# ==========================================================

def delete_alert(alert_id):

    alert = Alert.query.get(alert_id)

    if not alert:
        raise ValueError("Alert not found.")

    db.session.delete(alert)
    db.session.commit()

    return {
        "message": "Alert deleted successfully."
    }


# ==========================================================
# DASHBOARD COUNTS
# ==========================================================

def get_alert_counts():

    total = Alert.query.count()

    unread = Alert.query.filter_by(
        is_read=False
    ).count()

    resolved = Alert.query.filter_by(
        is_resolved=True
    ).count()

    critical = Alert.query.filter_by(
        severity="critical"
    ).count()

    warning = Alert.query.filter_by(
        severity="warning"
    ).count()

    info = Alert.query.filter_by(
        severity="info"
    ).count()

    return {
        "total": total,
        "unread": unread,
        "resolved": resolved,
        "critical": critical,
        "warning": warning,
        "info": info
    }


# ==========================================================
# FILTERS
# ==========================================================

def get_alerts_by_severity(severity):

    alerts = Alert.query.filter_by(
        severity=severity
    ).order_by(
        desc(Alert.created_at)
    ).all()

    return [
        alert.to_dict()
        for alert in alerts
    ]


def get_alerts_by_category(category):

    alerts = Alert.query.filter_by(
        category=category
    ).order_by(
        desc(Alert.created_at)
    ).all()

    return [
        alert.to_dict()
        for alert in alerts
    ]


def get_alert_history(limit=100):
    alerts = Alert.query.order_by(desc(Alert.created_at)).limit(limit).all()
    return [alert.to_dict() for alert in alerts]