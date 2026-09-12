from app.db import db
from datetime import datetime


class Footfall(db.Model):
    __tablename__ = "footfalls"

    id = db.Column(db.Integer, primary_key=True)

    device_id = db.Column(
        db.Integer,
        db.ForeignKey("devices.id")
    )

    entry_count = db.Column(
        db.Integer,
        default=0
    )

    exit_count = db.Column(
        db.Integer,
        default=0
    )

    current_occupancy = db.Column(db.Integer, default=0)
    dwell_time_avg = db.Column(db.Float, default=0.0)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    device = db.relationship(
        "Device",
        back_populates="footfalls"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "device_id": self.device.device_id if self.device else self.device_id,
            "entry_count": self.entry_count,
            "exit_count": self.exit_count,
            "current_occupancy": self.current_occupancy,
            "dwell_time_avg": self.dwell_time_avg,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }