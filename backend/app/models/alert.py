from app.db import db
from datetime import datetime


class Alert(db.Model):
    __tablename__ = "alerts"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(
        db.String(200),
        nullable=False
    )

    message = db.Column(
        db.Text,
        nullable=False
    )

    severity = db.Column(
        db.String(20),
        default="warning"
    )
    # info
    # warning
    # critical

    category = db.Column(
        db.String(50)
    )
    # inventory
    # queue
    # sensor
    # camera

    device_id = db.Column(
        db.Integer,
        db.ForeignKey("devices.id"),
        nullable=True
    )

    is_read = db.Column(
        db.Boolean,
        default=False
    )

    is_resolved = db.Column(
        db.Boolean,
        default=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    device = db.relationship(
        "Device",
        back_populates="alerts"
    )