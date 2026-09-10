from app.db import db
from datetime import datetime

class SensorReading(db.Model):
    __tablename__ = "sensor_readings"

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey("devices.id"), nullable=True, index=True)
    sensor_id_str = db.Column(db.String(100), nullable=False, index=True)
    sensor_type = db.Column(db.String(50), nullable=False, index=True)
    # Types: temperature, humidity, weight, ir_distance, motion_pir, ambient_light
    value = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), default="")  # °C, %, kg, cm, lux
    location = db.Column(db.String(100), default="Store Floor")
    threshold_min = db.Column(db.Float, nullable=True)
    threshold_max = db.Column(db.Float, nullable=True)
    is_anomaly = db.Column(db.Boolean, default=False, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Relationship
    device = db.relationship("Device", back_populates="sensor_readings")

    def to_dict(self):
        return {
            "id": self.id,
            "device_id": self.device_id,
            "sensor_id": self.sensor_id_str,
            "sensor_type": self.sensor_type,
            "value": round(float(self.value), 2) if self.value is not None else 0.0,
            "unit": self.unit or "",
            "location": self.location or "",
            "threshold_min": self.threshold_min,
            "threshold_max": self.threshold_max,
            "is_anomaly": bool(self.is_anomaly),
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }

