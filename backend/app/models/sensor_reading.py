from app.db import db
from datetime import datetime


class SensorReading(db.Model):
    __tablename__ = "sensor_readings"

    id = db.Column(db.Integer, primary_key=True)

    device_id = db.Column(
        db.Integer,
        db.ForeignKey("devices.id")
    )

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

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    device = db.relationship(
        "Device",
        back_populates="sensor_readings"
    )