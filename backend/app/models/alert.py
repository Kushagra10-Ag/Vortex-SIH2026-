from app.db import db
from datetime import datetime

class Alert(db.Model):
    __tablename__ = "alerts"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(30), default="info", index=True)  # info, warning, critical
    category = db.Column(db.String(50), default="system", index=True)
    # Categories: shelf_stock, theft_security, sensor_anomaly, device_offline, expiry_warning, footfall_surge, system

    source_device_id = db.Column(db.Integer, db.ForeignKey("devices.id"), nullable=True, index=True)

    is_read = db.Column(db.Boolean, default=False, index=True)
    is_resolved = db.Column(db.Boolean, default=False, index=True)
    resolved_at = db.Column(db.DateTime, nullable=True)
    resolved_by = db.Column(db.String(100), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Relationship
    device = db.relationship("Device", back_populates="alerts")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "message": self.message,
            "severity": self.severity,
            "category": self.category,
            "source_device_id": self.source_device_id,
            "device_name": self.device.name if self.device else None,
            "is_read": bool(self.is_read),
            "is_resolved": bool(self.is_resolved),
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "resolved_by": self.resolved_by or "",
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

