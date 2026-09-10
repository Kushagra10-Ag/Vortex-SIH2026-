from app.db import db
from datetime import datetime

class Device(db.Model):
    __tablename__ = "devices"

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    name = db.Column(db.String(150), nullable=False)
    device_type = db.Column(db.String(50), nullable=False, index=True)  # camera, sensor_hub, footfall_counter, edge_ai_box
    location = db.Column(db.String(100), default="Store Floor")
    ip_address = db.Column(db.String(50))
    mac_address = db.Column(db.String(50))
    status = db.Column(db.String(30), default="online", index=True)  # online, offline, warning, maintenance
    firmware_version = db.Column(db.String(50), default="1.0.0")
    last_heartbeat = db.Column(db.DateTime, default=datetime.utcnow)
    config_meta = db.Column(db.JSON, default=dict)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    camera_events = db.relationship("CameraEvent", back_populates="device", cascade="all, delete-orphan", lazy="dynamic")
    sensor_readings = db.relationship("SensorReading", back_populates="device", cascade="all, delete-orphan", lazy="dynamic")
    shelf_statuses = db.relationship("ShelfStatus", back_populates="device", lazy="dynamic")
    footfall_records = db.relationship("Footfall", back_populates="device", lazy="dynamic")
    alerts = db.relationship("Alert", back_populates="device", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "device_id": self.device_id,
            "name": self.name,
            "device_type": self.device_type,
            "location": self.location,
            "ip_address": self.ip_address or "",
            "mac_address": self.mac_address or "",
            "status": self.status,
            "firmware_version": self.firmware_version or "",
            "last_heartbeat": self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            "config_meta": self.config_meta or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

