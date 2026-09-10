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

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    device = db.relationship(
        "Device",
        back_populates="footfalls"
    )