from app.db import db
from datetime import datetime

class Footfall(db.Model):
    __tablename__ = "footfall"

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey("devices.id"), nullable=True, index=True)
    area_name = db.Column(db.String(100), default="Main Entrance", index=True)

    entry_count = db.Column(db.Integer, default=0)
    exit_count = db.Column(db.Integer, default=0)
    current_occupancy = db.Column(db.Integer, default=0)
    dwell_time_avg_seconds = db.Column(db.Float, default=0.0)

    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    hourly_bucket = db.Column(db.String(50), index=True)

    # Relationship
    device = db.relationship("Device", back_populates="footfall_records")

    def to_dict(self):
        return {
            "id": self.id,
            "device_id": self.device_id,
            "area_name": self.area_name,
            "entry_count": self.entry_count,
            "exit_count": self.exit_count,
            "current_occupancy": self.current_occupancy,
            "dwell_time_avg_seconds": round(float(self.dwell_time_avg_seconds or 0.0), 1),
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "hourly_bucket": self.hourly_bucket or "",
        }

