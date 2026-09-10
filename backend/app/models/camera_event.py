from app.db import db
from datetime import datetime

class CameraEvent(db.Model):
    __tablename__ = "camera_events"

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey("devices.id"), nullable=True, index=True)
    camera_id_str = db.Column(db.String(100), nullable=False, index=True)
    event_type = db.Column(db.String(100), nullable=False, index=True)
    # Types: person_detected, shelf_grab, queue_overflow, out_of_stock_detected, theft_alert, dwell_time_high
    confidence = db.Column(db.Float, default=0.95)
    snapshot_url = db.Column(db.Text)
    bbox_coordinates = db.Column(db.JSON, default=list)  # [x, y, w, h]
    details = db.Column(db.JSON, default=dict)  # extra metadata: person_count, shelf_id, dwell_seconds
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    device = db.relationship("Device", back_populates="camera_events")

    def to_dict(self):
        return {
            "id": self.id,
            "device_id": self.device_id,
            "camera_id": self.camera_id_str,
            "event_type": self.event_type,
            "confidence": round(float(self.confidence or 0.0), 3),
            "snapshot_url": self.snapshot_url or "",
            "bbox_coordinates": self.bbox_coordinates or [],
            "details": self.details or {},
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

