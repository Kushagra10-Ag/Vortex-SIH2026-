from app.db import db
from datetime import datetime


class CameraEvent(db.Model):
    __tablename__ = "camera_events"

    id = db.Column(db.Integer, primary_key=True)

    device_id = db.Column(
        db.Integer,
        db.ForeignKey("devices.id")
    )

    event_type = db.Column(
        db.String(50),
        nullable=False
    )
    # person_detected
    # queue_detected
    # shelf_scan
    # shelf_empty

    confidence = db.Column(
        db.Float,
        default=1.0
    )

    details = db.Column(
        db.JSON,
        default=dict
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    device = db.relationship(
        "Device",
        back_populates="camera_events"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "device_id": self.device.device_id if self.device else self.device_id,
            "event_type": self.event_type,
            "confidence": self.confidence,
            "details": self.details or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }