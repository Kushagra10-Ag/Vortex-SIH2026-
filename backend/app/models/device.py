from app.db import db
from datetime import datetime


class Device(db.Model):
    __tablename__ = "devices"

    id = db.Column(db.Integer, primary_key=True)

    device_id = db.Column(db.String(100), unique=True, nullable=False, index=True)

    name = db.Column(db.String(100), nullable=False)

    device_type = db.Column(
        db.String(50),
        nullable=False,
        index=True
    )  # camera, ir_sensor, ultrasonic_sensor

    location = db.Column(db.String(100), default="Store")

    status = db.Column(
        db.String(20),
        default="online"
    )  # online/offline

    last_heartbeat = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    camera_events = db.relationship(
        "CameraEvent",
        back_populates="device",
        cascade="all, delete-orphan"
    )

    sensor_readings = db.relationship(
        "SensorReading",
        back_populates="device",
        cascade="all, delete-orphan"
    )

    alerts = db.relationship(
        "Alert",
        back_populates="device"
    )

    footfalls = db.relationship(
        "Footfall",
        back_populates="device"
    )

    shelf_statuses = db.relationship(
        "ShelfStatus",
        back_populates="device"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "device_id": self.device_id,
            "name": self.name,
            "device_type": self.device_type,
            "location": self.location,
            "status": self.status,
            "last_heartbeat": self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }