from app.db import db
from datetime import datetime


class SensorReading(db.Model):
    __tablename__ = "sensor_readings"

    id = db.Column(db.Integer, primary_key=True)

    device_id = db.Column(
        db.Integer,
        db.ForeignKey("devices.id")
    )

    sensor_id = db.Column(db.String(100), nullable=False, index=True)

    sensor_type = db.Column(
        db.String(50),
        nullable=False,index=True
    )
    # ir
    # ultrasonic

    value = db.Column(
        db.Float,
        nullable=False
    )

    unit = db.Column(
        db.String(20)
    )

    is_mock = db.Column(
        db.Boolean,
        default=False
    )

    is_anomaly = db.Column(db.Boolean, default=False)
    threshold_min = db.Column(db.Float)
    threshold_max = db.Column(db.Float)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    device = db.relationship(
        "Device",
        back_populates="sensor_readings"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "device_id": self.device.device_id if self.device else self.device_id,
            "sensor_id": self.sensor_id,
            "sensor_type": self.sensor_type,
            "value": self.value,
            "unit": self.unit,
            "is_mock": self.is_mock,
            "is_anomaly": self.is_anomaly,
            "threshold_min": self.threshold_min,
            "threshold_max": self.threshold_max,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }